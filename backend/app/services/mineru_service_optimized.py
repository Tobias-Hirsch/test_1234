"""
优化的MinerU服务 - 集成VLM模式
用于替换现有的mineru_service.py，解决pipeline模式的GPU资源浪费问题

主要改进:
1. 使用VLM模式代替pipeline模式
2. 直接调用远程SGLang服务器
3. 保持与现有代码的兼容性
4. 添加详细的性能监控

使用方法:
1. 将此文件重命名为 mineru_service.py 替换现有文件
2. 或者在现有文件中导入 get_optimized_mineru_processor
3. 确保环境变量 MINERU_SGLANG_SERVER_URL 已配置

作者: Assistant
日期: 2025-01-26
"""

import logging
import asyncio
import aiohttp
import urllib.parse
import json
import base64
import time
from typing import Optional, Dict, Any, List, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)

# 尝试导入MinerU组件（用于PDF预处理）
try:
    from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2
    PDF_PREPROCESSING_AVAILABLE = True
    logger.info("PDF预处理功能可用 (PyPDFium2)")
except ImportError as e:
    logger.warning(f"PDF预处理功能不可用: {e}")
    PDF_PREPROCESSING_AVAILABLE = False
    
    # 提供降级方案
    def convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes: bytes) -> bytes:
        """降级方案：直接返回原始字节"""
        logger.debug("使用降级PDF预处理方案")
        return pdf_bytes


class OptimizedVLMProcessor:
    """
    优化的VLM处理器
    直接调用远程SGLang服务器，避免本地GPU资源浪费
    """
    
    def __init__(self):
        """初始化VLM处理器"""
        self.server_url = settings.MINERU_SGLANG_SERVER_URL
        
        if not self.server_url:
            logger.error("MINERU_SGLANG_SERVER_URL 未配置")
            logger.error("请在环境变量中设置: MINERU_SGLANG_SERVER_URL=http://1.116.119.85:8908")
            self.server_url = None
            return
        
        # 标准化URL
        parsed_url = urllib.parse.urlparse(self.server_url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # 配置参数
        self.timeout_seconds = 600  # 10分钟
        self.max_retries = 3
        self.retry_delay = 2.0
        
        logger.info(f"OptimizedVLMProcessor 初始化完成")
        logger.info(f"远程服务器: {self.base_url}")
        logger.info(f"超时设置: {self.timeout_seconds}秒")
        logger.info(f"重试设置: {self.max_retries}次")
    
    def _create_session(self) -> aiohttp.ClientSession:
        """创建HTTP会话"""
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        connector = aiohttp.TCPConnector(
            limit=10,
            limit_per_host=5,
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "RostiAI-MinerU-VLM/1.0",
            "Accept": "application/json"
        }
        
        return aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers
        )
    
    async def _check_server_health(self) -> bool:
        """检查服务器健康状态"""
        if not self.server_url:
            return False
        
        health_endpoints = ["/health", "/api/health", "/api/v1/health", "/status", "/"]
        
        try:
            async with self._create_session() as session:
                for endpoint in health_endpoints:
                    try:
                        async with session.get(f"{self.base_url}{endpoint}", timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                logger.debug(f"服务器健康检查成功: {endpoint}")
                                return True
                    except:
                        continue
        except Exception as e:
            logger.error(f"服务器健康检查失败: {e}")
        
        return False
    
    def _prepare_vlm_request(self, pdf_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        准备VLM请求数据
        返回多种可能的API格式以提高兼容性
        """
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # 主要格式
        primary_format = {
            "endpoint": "/api/v1/parse_pdf",
            "data": {
                "file_data": pdf_b64,
                "filename": filename,
                "mode": "vlm",
                "backend": "sglang",
                "config": {
                    "formula_enable": True,
                    "table_enable": True,
                    "parse_method": "auto",
                    "lang": "auto"
                }
            }
        }
        
        # 备用格式
        alternative_formats = [
            {
                "endpoint": "/api/v1/vlm/parse",
                "data": {
                    "pdf_data": pdf_b64,
                    "filename": filename,
                    "options": {
                        "parse_formulas": True,
                        "parse_tables": True,
                        "language": "auto"
                    }
                }
            },
            {
                "endpoint": "/api/parse",
                "data": {
                    "document": pdf_b64,
                    "name": filename,
                    "type": "pdf",
                    "backend": "vlm-sglang"
                }
            },
            {
                "endpoint": "/parse",
                "data": {
                    "file": pdf_b64,
                    "filename": filename,
                    "parser": "mineru-vlm"
                }
            }
        ]
        
        return [primary_format] + alternative_formats
    
    async def _vlm_parse_request(
        self, 
        session: aiohttp.ClientSession, 
        endpoint: str, 
        request_data: Dict[str, Any],
        filename: str
    ) -> Optional[Dict[str, Any]]:
        """执行单次VLM解析请求"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"VLM请求: {endpoint}")
            start_time = time.time()
            
            async with session.post(url, json=request_data) as response:
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"VLM解析成功: {filename} (耗时: {processing_time:.2f}s)")
                    
                    # 标准化结果格式
                    return self._standardize_result(result, filename, processing_time)
                
                elif response.status == 404:
                    logger.debug(f"端点不存在: {endpoint}")
                    return None
                
                else:
                    error_text = await response.text()
                    logger.warning(f"VLM请求失败 {response.status}: {error_text[:200]}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"VLM请求超时: {endpoint}")
            return None
        except Exception as e:
            logger.error(f"VLM请求异常: {endpoint} - {e}")
            return None
    
    def _standardize_result(self, raw_result: Any, filename: str, processing_time: float) -> Dict[str, Any]:
        """
        标准化解析结果，确保与现有系统兼容
        
        现有系统期望的格式:
        {
            "result": [...] # 内容列表
        }
        """
        if not raw_result:
            logger.warning(f"VLM返回空结果: {filename}")
            return {"result": []}
        
        # 如果已经是标准格式
        if isinstance(raw_result, dict) and "result" in raw_result:
            logger.debug(f"结果已是标准格式: {filename}")
            return raw_result
        
        # 提取内容列表
        content_list = []
        
        if isinstance(raw_result, list):
            content_list = raw_result
            logger.debug(f"结果是直接列表格式: {len(content_list)} 项")
        
        elif isinstance(raw_result, dict):
            # 尝试多种可能的字段名
            content_keys = ["content", "result", "data", "content_list", "parsed_content", "blocks"]
            
            for key in content_keys:
                if key in raw_result and isinstance(raw_result[key], list):
                    content_list = raw_result[key]
                    logger.debug(f"从字段 '{key}' 提取内容: {len(content_list)} 项")
                    break
        
        # 构建标准结果
        result = {"result": content_list}
        
        # 添加元数据（可选，用于调试）
        if isinstance(raw_result, dict):
            metadata = {
                "filename": filename,
                "processing_time": processing_time,
                "mode": "vlm-optimized",
                "content_blocks": len(content_list)
            }
            
            # 保留错误信息
            if "errors" in raw_result:
                metadata["errors"] = raw_result["errors"]
            if "warnings" in raw_result:
                metadata["warnings"] = raw_result["warnings"]
            
            result["_metadata"] = metadata
        
        logger.info(f"标准化结果: {filename} - {len(content_list)} 内容块")
        return result
    
    async def process_document_bytes(self, file_bytes: bytes, filename: str, strategy: str = "vlm") -> Optional[Dict[str, Any]]:
        """
        处理文档字节数据 - 主要接口方法
        
        Args:
            file_bytes: 文件字节数据
            filename: 文件名
            strategy: 处理策略（忽略，总是使用VLM）
            
        Returns:
            解析结果字典 {"result": [...]} 或 None
        """
        if not file_bytes:
            logger.error(f"文件数据为空: {filename}")
            return None
        
        if not self.server_url:
            logger.error(f"远程服务器未配置，无法处理: {filename}")
            return None
        
        file_size_mb = len(file_bytes) / 1024 / 1024
        logger.info(f"开始VLM处理: {filename} ({file_size_mb:.2f} MB)")
        
        # PDF预处理（如果可用）
        if filename.lower().endswith('.pdf') and PDF_PREPROCESSING_AVAILABLE:
            try:
                logger.debug(f"应用PDF预处理: {filename}")
                file_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(file_bytes)
                logger.debug(f"PDF预处理完成: {filename}")
            except Exception as e:
                logger.warning(f"PDF预处理失败，使用原始数据: {filename} - {e}")
        
        # 检查服务器状态
        if not await self._check_server_health():
            logger.error(f"远程服务器不可用: {filename}")
            return None
        
        # 准备请求格式
        request_formats = self._prepare_vlm_request(file_bytes, filename)
        
        # 尝试不同的API格式
        async with self._create_session() as session:
            for i, format_config in enumerate(request_formats, 1):
                logger.debug(f"尝试格式 {i}/{len(request_formats)}: {format_config['endpoint']}")
                
                result = await self._vlm_parse_request(
                    session, 
                    format_config["endpoint"], 
                    format_config["data"],
                    filename
                )
                
                if result:
                    logger.info(f"VLM处理成功: {filename} (格式 {i})")
                    return result
                
                # 在格式之间短暂等待
                if i < len(request_formats):
                    await asyncio.sleep(0.5)
        
        logger.error(f"所有VLM格式都失败: {filename}")
        return None


class LocalMinerUParser:
    """
    本地MinerU解析器 - 兼容性包装
    在无法使用远程服务时的降级方案
    """
    
    def __init__(self):
        logger.warning("LocalMinerUParser 作为降级方案初始化")
        logger.warning("建议配置 MINERU_SGLANG_SERVER_URL 使用优化的VLM模式")
    
    async def process_document_bytes(self, file_bytes: bytes, filename: str, strategy: str = "pipeline") -> Optional[Dict[str, Any]]:
        """降级处理方法"""
        logger.error(f"本地处理不可用: {filename}")
        logger.error("请配置远程SGLang服务器或安装本地MinerU依赖")
        return None


class MinerUClient:
    """
    旧的MinerU客户端 - 兼容性包装
    重定向到优化的VLM处理器
    """
    
    def __init__(self):
        self.optimized_processor = OptimizedVLMProcessor()
        logger.info("MinerUClient 重定向到优化VLM处理器")
    
    async def process_document_bytes(self, file_bytes: bytes, filename: str, strategy: str) -> Optional[Dict[str, Any]]:
        """重定向到优化处理器"""
        return await self.optimized_processor.process_document_bytes(file_bytes, filename, "vlm")


# 全局处理器实例
_mineru_processor = None

def get_mineru_processor():
    """
    获取MinerU处理器实例 - 兼容现有代码
    现在默认返回优化的VLM处理器
    """
    global _mineru_processor
    
    if _mineru_processor is None:
        # 检查配置
        if settings.MINERU_SGLANG_SERVER_URL:
            logger.info("使用优化VLM处理器 (推荐)")
            _mineru_processor = OptimizedVLMProcessor()
        else:
            logger.warning("未配置远程服务器，使用降级方案")
            logger.warning("请设置 MINERU_SGLANG_SERVER_URL=http://1.116.119.85:8908")
            _mineru_processor = LocalMinerUParser()
    
    return _mineru_processor


# 创建全局客户端实例 - 兼容现有代码
mineru_client = get_mineru_processor()

# 导出兼容接口
__all__ = [
    "get_mineru_processor",
    "mineru_client", 
    "OptimizedVLMProcessor",
    "LocalMinerUParser",
    "MinerUClient"
]