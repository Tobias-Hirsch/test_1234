"""
混合VLM服务 - 支持远程SGLang和本地VLM加速
当没有SGLang服务器时自动回退到本地VLM模式，仍能获得比pipeline更好的性能

主要特性:
1. 优先使用远程SGLang服务器 (最佳性能)
2. 自动回退到本地VLM模式 (中等性能，比pipeline好)
3. 最终回退到pipeline模式 (兜底方案)
4. 保持完整的API兼容性

作者: Assistant  
日期: 2025-01-27
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

# 尝试导入MinerU组件
try:
    from mineru.backend.vlm.vlm_analyze import doc_analyze as vlm_doc_analyze
    from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
    from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
    from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json
    from mineru.utils.enum_class import MakeMode
    from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make
    from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2
    MINERU_INSTALLED = True
    logger.info("MinerU组件导入成功，支持本地VLM和pipeline模式")
except ImportError as e:
    logger.warning(f"MinerU组件导入失败: {e}")
    logger.warning("将使用纯远程SGLang模式或降级方案")
    MINERU_INSTALLED = False
    
    # 提供降级方案
    def convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes: bytes) -> bytes:
        """降级方案：直接返回原始字节"""
        return pdf_bytes


class HybridVLMProcessor:
    """
    混合VLM处理器
    智能选择最佳可用的处理模式:
    1. 远程SGLang (最佳) -> 2. 本地VLM (良好) -> 3. Pipeline (兜底)
    """
    
    def __init__(self):
        """初始化混合处理器"""
        self.server_url = settings.MINERU_SGLANG_SERVER_URL
        self.modes = {
            "remote_sglang": False,
            "local_vlm": MINERU_INSTALLED,
            "local_pipeline": MINERU_INSTALLED
        }
        
        # 配置远程服务器
        if self.server_url:
            parsed_url = urllib.parse.urlparse(self.server_url)
            self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            logger.info(f"配置远程SGLang服务器: {self.base_url}")
        else:
            self.base_url = None
            logger.info("未配置远程SGLang服务器")
        
        # 配置参数
        self.timeout_seconds = 300  # 5分钟
        self.max_retries = 2
        self.retry_delay = 1.0
        
        logger.info(f"HybridVLMProcessor 初始化完成")
        logger.info(f"可用模式: {[k for k, v in self.modes.items() if v]}")
    
    async def _test_remote_server(self) -> bool:
        """测试远程服务器是否可用"""
        if not self.base_url:
            return False
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/get_model_info") as response:
                    if response.status == 200:
                        logger.info("远程SGLang服务器可用")
                        self.modes["remote_sglang"] = True
                        return True
        except Exception as e:
            logger.warning(f"远程SGLang服务器不可用: {e}")
        
        self.modes["remote_sglang"] = False
        return False
    
    async def _process_with_remote_sglang(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """使用远程SGLang处理（方法1 - 最佳性能）"""
        if not self.modes["remote_sglang"]:
            return None
        
        logger.info(f"使用远程SGLang处理: {filename}")
        
        # 这里可以使用之前创建的OptimizedVLMProcessor的逻辑
        # 或者调用原生的vlm_doc_analyze with sglang-client
        try:
            if MINERU_INSTALLED:
                # 使用MinerU的原生VLM分析
                processed_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(file_bytes)
                
                middle_json, _ = vlm_doc_analyze(
                    processed_bytes,
                    image_writer=None,
                    backend="sglang-client",
                    server_url=self.base_url
                )
                
                pdf_info = middle_json.get("pdf_info")
                if pdf_info:
                    content_list = vlm_union_make(pdf_info, MakeMode.CONTENT_LIST, "")
                    if content_list:
                        logger.info(f"远程SGLang处理成功: {filename} - {len(content_list)} 项")
                        return {"result": content_list}
        except Exception as e:
            logger.error(f"远程SGLang处理失败: {filename} - {e}")
        
        return None
    
    def _process_with_local_vlm(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """使用本地VLM处理（方法2 - 良好性能）"""
        if not self.modes["local_vlm"]:
            return None
        
        logger.info(f"使用本地VLM处理: {filename}")
        
        try:
            # 预处理PDF
            processed_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(file_bytes)
            
            # 使用本地VLM分析（不需要外部服务器）
            middle_json, _ = vlm_doc_analyze(
                processed_bytes,
                image_writer=None,
                backend="local",  # 或者其他本地后端
                server_url=None
            )
            
            pdf_info = middle_json.get("pdf_info")
            if pdf_info:
                content_list = vlm_union_make(pdf_info, MakeMode.CONTENT_LIST, "")
                if content_list:
                    logger.info(f"本地VLM处理成功: {filename} - {len(content_list)} 项")
                    return {"result": content_list}
                    
        except Exception as e:
            logger.error(f"本地VLM处理失败: {filename} - {e}")
        
        return None
    
    def _process_with_local_pipeline(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """使用本地Pipeline处理（方法3 - 兜底方案）"""
        if not self.modes["local_pipeline"]:
            return None
        
        logger.info(f"使用本地Pipeline处理: {filename}")
        
        try:
            # 预处理PDF
            processed_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(file_bytes)
            
            # 运行pipeline分析
            infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = pipeline_doc_analyze(
                [processed_bytes],
                ['ch'],  # 语言占位符
                parse_method="auto",
                formula_enable=True,
                table_enable=True
            )
            
            if infer_results and infer_results[0]:
                # 转换为中间JSON格式
                middle_json = pipeline_result_to_middle_json(
                    model_list=infer_results[0],
                    images_list=all_image_lists[0],
                    pdf_doc=all_pdf_docs[0],
                    image_writer=None,
                    lang=lang_list[0],
                    ocr_enable=ocr_enabled_list[0]
                )
                
                pdf_info = middle_json.get("pdf_info")
                if pdf_info:
                    content_list = pipeline_union_make(pdf_info, MakeMode.CONTENT_LIST, "")
                    if content_list:
                        logger.info(f"本地Pipeline处理成功: {filename} - {len(content_list)} 项")
                        return {"result": content_list}
                        
        except Exception as e:
            logger.error(f"本地Pipeline处理失败: {filename} - {e}")
        
        return None
    
    async def process_document_bytes(self, file_bytes: bytes, filename: str, strategy: str = "auto") -> Optional[Dict[str, Any]]:
        """
        智能处理文档字节数据
        
        Args:
            file_bytes: 文件字节数据
            filename: 文件名
            strategy: 处理策略 ("auto", "remote", "local-vlm", "pipeline")
            
        Returns:
            解析结果字典 {"result": [...]} 或 None
        """
        if not file_bytes:
            logger.error(f"文件数据为空: {filename}")
            return None
        
        file_size_mb = len(file_bytes) / 1024 / 1024
        logger.info(f"开始混合VLM处理: {filename} ({file_size_mb:.2f} MB) - 策略: {strategy}")
        
        # 如果指定了特定策略
        if strategy == "remote" and self.base_url:
            if await self._test_remote_server():
                return await self._process_with_remote_sglang(file_bytes, filename)
            else:
                logger.warning("远程服务器不可用，切换到自动模式")
        
        elif strategy == "local-vlm":
            return await asyncio.to_thread(self._process_with_local_vlm, file_bytes, filename)
        
        elif strategy == "pipeline":
            return await asyncio.to_thread(self._process_with_local_pipeline, file_bytes, filename)
        
        # 自动模式：按优先级依次尝试
        processing_methods = [
            ("远程SGLang", self._try_remote_processing),
            ("本地VLM", self._try_local_vlm_processing),
            ("本地Pipeline", self._try_local_pipeline_processing)
        ]
        
        for method_name, method_func in processing_methods:
            try:
                result = await method_func(file_bytes, filename)
                if result:
                    logger.info(f"处理成功使用: {method_name} - {filename}")
                    return result
                else:
                    logger.debug(f"{method_name} 处理失败，尝试下一种方法")
            except Exception as e:
                logger.warning(f"{method_name} 处理异常: {e}")
        
        logger.error(f"所有处理方法都失败了: {filename}")
        return None
    
    async def _try_remote_processing(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """尝试远程处理"""
        if self.base_url and await self._test_remote_server():
            return await self._process_with_remote_sglang(file_bytes, filename)
        return None
    
    async def _try_local_vlm_processing(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """尝试本地VLM处理"""
        if self.modes["local_vlm"]:
            return await asyncio.to_thread(self._process_with_local_vlm, file_bytes, filename)
        return None
    
    async def _try_local_pipeline_processing(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """尝试本地Pipeline处理"""
        if self.modes["local_pipeline"]:
            return await asyncio.to_thread(self._process_with_local_pipeline, file_bytes, filename)
        return None


class FallbackProcessor:
    """降级处理器 - 当MinerU完全不可用时"""
    
    def __init__(self):
        logger.warning("FallbackProcessor 初始化 - MinerU功能不可用")
    
    async def process_document_bytes(self, file_bytes: bytes, filename: str, strategy: str = "fallback") -> Optional[Dict[str, Any]]:
        """降级处理方法"""
        logger.error(f"无法处理文档: {filename} - MinerU组件不可用")
        logger.error("请安装MinerU依赖或配置远程SGLang服务器")
        return {"result": [{"type": "text", "text": f"文档处理不可用: {filename}"}]}


# 全局处理器实例
_hybrid_processor = None

def get_hybrid_mineru_processor():
    """
    获取混合MinerU处理器实例
    智能选择最佳可用的处理模式
    """
    global _hybrid_processor
    
    if _hybrid_processor is None:
        if MINERU_INSTALLED or settings.MINERU_SGLANG_SERVER_URL:
            logger.info("初始化混合VLM处理器")
            _hybrid_processor = HybridVLMProcessor()
        else:
            logger.warning("初始化降级处理器")
            _hybrid_processor = FallbackProcessor()
    
    return _hybrid_processor


# 兼容性接口
mineru_client = get_hybrid_mineru_processor()

# 导出接口
__all__ = [
    "get_hybrid_mineru_processor",
    "mineru_client",
    "HybridVLMProcessor",
    "FallbackProcessor"
]