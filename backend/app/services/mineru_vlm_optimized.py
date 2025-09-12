"""
优化的MinerU VLM服务实现
直接调用远程SGLang服务器，不依赖本地mineru[all]安装

特点:
1. 使用VLM模式，避免pipeline模式的GPU资源浪费
2. 支持异步处理和重连机制
3. 集成到现有的Rosti系统架构中
4. 提供详细的性能监控和错误处理

作者: Assistant
日期: 2025-01-26
"""

import asyncio
import aiohttp
import json
import logging
import time
import base64
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import urllib.parse

from app.core.config import settings

logger = logging.getLogger(__name__)

class OptimizedMinerUVLMClient:
    """
    优化的MinerU VLM客户端
    直接调用远程SGLang服务器，避免本地GPU资源浪费
    """
    
    def __init__(self, server_url: Optional[str] = None):
        """
        初始化VLM客户端
        
        Args:
            server_url: SGLang服务器URL，默认从配置获取
        """
        self.server_url = server_url or settings.MINERU_SGLANG_SERVER_URL
        if not self.server_url:
            raise ValueError("MINERU_SGLANG_SERVER_URL 未配置")
        
        # 标准化URL
        parsed_url = urllib.parse.urlparse(self.server_url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # 配置选项
        self.timeout = aiohttp.ClientTimeout(total=600)  # 10分钟超时
        self.max_retries = 3
        self.retry_delay = 2.0  # 秒
        
        logger.info(f"初始化OptimizedMinerUVLMClient: {self.base_url}")
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """创建HTTP客户端会话"""
        return aiohttp.ClientSession(
            timeout=self.timeout,
            connector=aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                keepalive_timeout=60,
                enable_cleanup_closed=True
            ),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "RostiAI-MinerU-VLM-Client/1.0"
            }
        )
    
    async def check_server_health(self) -> Tuple[bool, Dict[str, Any]]:
        """
        检查远程服务器健康状态
        
        Returns:
            (is_healthy, server_info)
        """
        health_endpoints = ["/health", "/api/health", "/api/v1/health", "/status"]
        
        async with await self._create_session() as session:
            for endpoint in health_endpoints:
                try:
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        if response.status == 200:
                            try:
                                data = await response.json()
                                logger.info(f"服务器健康检查成功: {endpoint}")
                                return True, data
                            except:
                                logger.info(f"服务器响应正常但非JSON格式: {endpoint}")
                                return True, {"status": "ok", "endpoint": endpoint}
                except Exception as e:
                    logger.debug(f"健康检查失败 {endpoint}: {e}")
                    continue
        
        logger.warning("所有健康检查端点都失败")
        return False, {}
    
    async def _discover_parse_endpoint(self, session: aiohttp.ClientSession) -> Optional[str]:
        """
        自动发现可用的解析API端点
        
        Returns:
            可用的端点URL或None
        """
        candidate_endpoints = [
            "/api/v1/parse_pdf",
            "/api/v1/vlm/parse", 
            "/api/v1/parse",
            "/api/parse",
            "/parse",
            "/api/v1/document/parse",
            "/api/v1/mineru/parse"
        ]
        
        for endpoint in candidate_endpoints:
            try:
                # 发送简单的POST请求测试端点
                test_data = {"test": "endpoint_discovery"}
                async with session.post(f"{self.base_url}{endpoint}", json=test_data) as response:
                    # 如果不是404，说明端点存在
                    if response.status != 404:
                        logger.info(f"发现可用解析端点: {endpoint} (状态: {response.status})")
                        return endpoint
                        
            except Exception as e:
                logger.debug(f"端点测试失败 {endpoint}: {e}")
                continue
        
        logger.warning("未找到可用的解析端点")
        return None
    
    def _prepare_request_data(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        准备API请求数据
        支持多种可能的API格式
        
        Args:
            pdf_bytes: PDF文件字节数据
            filename: 文件名
            
        Returns:
            请求数据字典
        """
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # 标准请求格式
        return {
            "file_data": pdf_b64,
            "filename": filename,
            "mode": "vlm",
            "backend": "sglang",
            "config": {
                "formula_enable": True,
                "table_enable": True,
                "parse_method": "auto",
                "lang": "auto",  # 自动检测语言
                "output_format": "json"
            },
            "options": {
                "extract_images": False,  # 减少数据传输
                "extract_tables": True,
                "extract_formulas": True,
                "preserve_layout": True
            }
        }
    
    def _prepare_alternative_formats(self, pdf_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        准备备用API请求格式
        
        Returns:
            备用请求格式列表
        """
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return [
            # 格式1: 简化版
            {
                "pdf_data": pdf_b64,
                "filename": filename,
                "vlm_mode": True
            },
            
            # 格式2: MinerU标准格式
            {
                "document": pdf_b64,
                "name": filename,
                "type": "pdf",
                "backend": "vlm-sglang",
                "parse_options": {
                    "formula": True,
                    "table": True
                }
            },
            
            # 格式3: 通用格式
            {
                "file": pdf_b64,
                "filename": filename,
                "parser": "mineru-vlm",
                "settings": {
                    "mode": "vlm",
                    "engine": "sglang"
                }
            }
        ]
    
    async def _parse_with_endpoint(
        self, 
        session: aiohttp.ClientSession, 
        endpoint: str, 
        request_data: Dict[str, Any],
        filename: str
    ) -> Optional[Dict[str, Any]]:
        """
        使用指定端点进行解析
        
        Args:
            session: HTTP会话
            endpoint: API端点
            request_data: 请求数据
            filename: 文件名（用于日志）
            
        Returns:
            解析结果或None
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.info(f"开始VLM解析: {filename} -> {endpoint}")
            start_time = time.time()
            
            async with session.post(url, json=request_data) as response:
                processing_time = time.time() - start_time
                
                logger.info(f"API响应: {response.status} (耗时: {processing_time:.2f}s)")
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"VLM解析成功: {filename}")
                    
                    # 标准化结果格式
                    standardized_result = self._standardize_result(result, filename, processing_time)
                    return standardized_result
                    
                else:
                    error_text = await response.text()
                    logger.warning(f"API错误 {response.status}: {error_text[:200]}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"解析超时: {filename} -> {endpoint}")
            return None
        except Exception as e:
            logger.error(f"解析异常: {filename} -> {endpoint}: {e}")
            return None
    
    def _standardize_result(self, raw_result: Any, filename: str, processing_time: float) -> Dict[str, Any]:
        """
        标准化解析结果格式，确保与现有系统兼容
        
        Args:
            raw_result: 原始解析结果
            filename: 文件名
            processing_time: 处理时间
            
        Returns:
            标准化的结果字典
        """
        if not raw_result:
            return {"result": [], "metadata": {"error": "Empty result"}}
        
        # 如果结果已经是标准格式
        if isinstance(raw_result, dict) and "result" in raw_result:
            return raw_result
        
        # 尝试提取内容列表
        content_list = []
        
        if isinstance(raw_result, list):
            content_list = raw_result
        elif isinstance(raw_result, dict):
            # 尝试多个可能的字段名
            for key in ["content", "result", "data", "content_list", "parsed_content"]:
                if key in raw_result:
                    content_candidate = raw_result[key]
                    if isinstance(content_candidate, list):
                        content_list = content_candidate
                        break
        
        # 构建标准结果
        standardized = {
            "result": content_list,
            "metadata": {
                "filename": filename,
                "processing_time": processing_time,
                "mode": "vlm",
                "backend": "sglang-remote",
                "content_blocks": len(content_list),
                "raw_result_type": type(raw_result).__name__
            }
        }
        
        # 添加错误信息（如果有）
        if isinstance(raw_result, dict):
            if "errors" in raw_result:
                standardized["metadata"]["errors"] = raw_result["errors"]
            if "warnings" in raw_result:
                standardized["metadata"]["warnings"] = raw_result["warnings"]
        
        return standardized
    
    async def process_document_bytes(self, file_bytes: bytes, filename: str, strategy: str = "vlm") -> Optional[Dict[str, Any]]:
        """
        处理PDF文档字节数据
        主要的公共接口方法，与现有MinerU服务兼容
        
        Args:
            file_bytes: PDF文件字节数据
            filename: 文件名
            strategy: 处理策略（忽略，始终使用VLM）
            
        Returns:
            解析结果字典或None
        """
        if not file_bytes:
            logger.error(f"文件数据为空: {filename}")
            return None
        
        file_size_mb = len(file_bytes) / 1024 / 1024
        logger.info(f"开始处理文档: {filename} ({file_size_mb:.2f} MB)")
        
        # 检查服务器健康状态
        is_healthy, server_info = await self.check_server_health()
        if not is_healthy:
            logger.error(f"远程服务器不可用: {filename}")
            return None
        
        async with await self._create_session() as session:
            # 发现可用的解析端点
            endpoint = await self._discover_parse_endpoint(session)
            if not endpoint:
                logger.error(f"未找到可用的解析端点: {filename}")
                return None
            
            # 准备请求数据
            main_request = self._prepare_request_data(file_bytes, filename)
            
            # 尝试主要格式
            result = await self._parse_with_endpoint(session, endpoint, main_request, filename)
            if result:
                return result
            
            # 尝试备用格式
            logger.info(f"主要格式失败，尝试备用格式: {filename}")
            alternative_formats = self._prepare_alternative_formats(file_bytes, filename)
            
            for i, alt_format in enumerate(alternative_formats, 1):
                logger.info(f"尝试备用格式 {i}/{len(alternative_formats)}: {filename}")
                result = await self._parse_with_endpoint(session, endpoint, alt_format, filename)
                if result:
                    return result
            
            logger.error(f"所有解析尝试都失败: {filename}")
            return None


# 工厂函数，与现有系统集成
def create_optimized_vlm_processor() -> OptimizedMinerUVLMClient:
    """
    创建优化的VLM处理器实例
    可以替代现有的MinerU处理器
    
    Returns:
        OptimizedMinerUVLMClient实例
    """
    try:
        return OptimizedMinerUVLMClient()
    except ValueError as e:
        logger.error(f"无法创建VLM处理器: {e}")
        logger.error("请确保在环境变量或.env文件中设置 MINERU_SGLANG_SERVER_URL")
        raise


# 兼容性包装器
class OptimizedMinerUProcessor:
    """
    兼容现有MinerU服务接口的包装器
    可以直接替换现有的get_mineru_processor()返回值
    """
    
    def __init__(self):
        self.vlm_client = OptimizedMinerUVLMClient()
        logger.info("OptimizedMinerUProcessor 初始化完成")
    
    async def process_document_bytes(self, file_bytes: bytes, filename: str, strategy: str = "vlm") -> Optional[Dict[str, Any]]:
        """
        与现有接口兼容的文档处理方法
        
        Args:
            file_bytes: 文件字节数据
            filename: 文件名 
            strategy: 处理策略（始终使用VLM优化）
            
        Returns:
            处理结果
        """
        logger.info(f"使用优化VLM模式处理文档: {filename} (策略: {strategy})")
        return await self.vlm_client.process_document_bytes(file_bytes, filename, "vlm")


# 全局单例实例
_optimized_processor = None

def get_optimized_mineru_processor():
    """
    获取优化的MinerU处理器单例
    可以直接替换mineru_service.py中的get_mineru_processor()
    
    Returns:
        OptimizedMinerUProcessor实例
    """
    global _optimized_processor
    if _optimized_processor is None:
        _optimized_processor = OptimizedMinerUProcessor()
        logger.info("创建优化MinerU处理器单例")
    return _optimized_processor