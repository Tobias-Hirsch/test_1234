"""
统一MinerU处理器服务
整合所有MinerU相关处理策略，提供统一接口

主要特性：
1. 智能策略选择（SGLang、VLM、Pipeline、Fallback）
2. 统一错误处理和重试机制
3. 性能监控和日志记录
4. 配置验证和环境适应
5. 向后兼容现有API

作者: Assistant
日期: 2025-01-26
版本: 1.0
"""

import logging
import asyncio
import aiohttp
import urllib.parse
import json
import base64
import time
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

# 尝试导入MinerU组件
try:
    from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2
    PDF_PREPROCESSING_AVAILABLE = True
    logger.info("PDF预处理功能可用 (PyPDFium2)")
except ImportError as e:
    logger.warning(f"PDF预处理功能不可用: {e}")
    PDF_PREPROCESSING_AVAILABLE = False
    
    def convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes: bytes) -> bytes:
        """降级方案：直接返回原始字节"""
        logger.debug("使用降级PDF预处理方案")
        return pdf_bytes


class ProcessingStrategy:
    """处理策略基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.success_count = 0
        self.failure_count = 0
        self.total_processing_time = 0.0
    
    async def process(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """处理文档的抽象方法"""
        raise NotImplementedError("子类必须实现process方法")
    
    def get_success_rate(self) -> float:
        """计算成功率"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    def get_average_processing_time(self) -> float:
        """计算平均处理时间"""
        return self.total_processing_time / self.success_count if self.success_count > 0 else 0.0
    
    def record_success(self, processing_time: float):
        """记录成功处理"""
        self.success_count += 1
        self.total_processing_time += processing_time
    
    def record_failure(self):
        """记录失败处理"""
        self.failure_count += 1


class SGLangStrategy(ProcessingStrategy):
    """SGLang远程服务处理策略"""
    
    def __init__(self):
        super().__init__("sglang")
        self.server_url = settings.MINERU_SGLANG_SERVER_URL
        self.timeout_seconds = 600
        self.max_retries = 3
        
        if self.server_url:
            parsed_url = urllib.parse.urlparse(self.server_url)
            self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        else:
            self.base_url = None
    
    async def process(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """SGLang远程处理"""
        if not self.base_url:
            logger.error("SGLang服务器URL未配置")
            return None
        
        start_time = time.time()
        
        try:
            # 检查服务器健康状态
            if not await self._check_server_health():
                logger.error("SGLang服务器不可用")
                self.record_failure()
                return None
            
            # 准备请求数据
            pdf_b64 = base64.b64encode(file_bytes).decode('utf-8')
            request_data = {
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
            
            # 执行请求
            async with self._create_session() as session:
                async with session.post(f"{self.base_url}/api/v1/parse_pdf", json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        processing_time = time.time() - start_time
                        self.record_success(processing_time)
                        
                        logger.info(f"SGLang处理成功: {filename} (耗时: {processing_time:.2f}s)")
                        return self._standardize_result(result, filename)
                    else:
                        error_text = await response.text()
                        logger.error(f"SGLang处理失败 {response.status}: {error_text[:200]}")
                        self.record_failure()
                        return None
        
        except Exception as e:
            logger.error(f"SGLang处理异常: {filename} - {e}")
            self.record_failure()
            return None
    
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
            "User-Agent": "RostiAI-MinerU-Unified/1.0",
            "Accept": "application/json"
        }
        
        return aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=headers
        )
    
    async def _check_server_health(self) -> bool:
        """检查服务器健康状态"""
        health_endpoints = ["/health", "/api/health", "/api/v1/health", "/status", "/"]
        
        try:
            async with self._create_session() as session:
                for endpoint in health_endpoints:
                    try:
                        async with session.get(f"{self.base_url}{endpoint}", timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                logger.debug(f"SGLang服务器健康检查成功: {endpoint}")
                                return True
                    except:
                        continue
        except Exception as e:
            logger.error(f"SGLang服务器健康检查失败: {e}")
        
        return False
    
    def _standardize_result(self, raw_result: Any, filename: str) -> Dict[str, Any]:
        """标准化结果格式"""
        if not raw_result:
            return {"result": []}
        
        # 如果已经是标准格式
        if isinstance(raw_result, dict) and "result" in raw_result:
            return raw_result
        
        # 提取内容列表
        content_list = []
        if isinstance(raw_result, list):
            content_list = raw_result
        elif isinstance(raw_result, dict):
            content_keys = ["content", "result", "data", "content_list", "parsed_content", "blocks"]
            for key in content_keys:
                if key in raw_result and isinstance(raw_result[key], list):
                    content_list = raw_result[key]
                    break
        
        return {"result": content_list}


class VLMStrategy(ProcessingStrategy):
    """本地VLM处理策略"""
    
    def __init__(self):
        super().__init__("vlm")
        # VLM处理逻辑（如果需要本地VLM支持）
    
    async def process(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """本地VLM处理（占位符实现）"""
        logger.info(f"VLM处理策略尚未完全实现: {filename}")
        self.record_failure()
        return None


class PipelineStrategy(ProcessingStrategy):
    """Pipeline处理策略"""
    
    def __init__(self):
        super().__init__("pipeline")
    
    async def process(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """Pipeline处理（占位符实现）"""
        logger.info(f"Pipeline处理策略尚未完全实现: {filename}")
        self.record_failure()
        return None


class FallbackStrategy(ProcessingStrategy):
    """降级处理策略 - PyMuPDF"""
    
    def __init__(self):
        super().__init__("fallback")
    
    async def process(self, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """PyMuPDF降级处理"""
        try:
            import fitz  # PyMuPDF
            
            start_time = time.time()
            
            # 使用PyMuPDF提取文本
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    full_text += f"\n\n--- 第{page_num + 1}页 ---\n{page_text}"
            
            doc.close()
            
            if full_text.strip():
                processing_time = time.time() - start_time
                self.record_success(processing_time)
                
                # 构造标准结果格式
                result = {
                    "result": [
                        {
                            "type": "text",
                            "text": full_text.strip(),
                            "page_idx": 0
                        }
                    ]
                }
                
                logger.info(f"Fallback处理成功: {filename} (耗时: {processing_time:.2f}s)")
                return result
            else:
                logger.warning(f"Fallback处理未提取到文本: {filename}")
                self.record_failure()
                return None
                
        except Exception as e:
            logger.error(f"Fallback处理失败: {filename} - {e}")
            self.record_failure()
            return None


class MinerUConfig:
    """MinerU配置管理类"""
    
    @classmethod
    def get_processing_strategy(cls) -> str:
        """智能选择处理策略"""
        # 强制模式检查
        if settings.MINERU_FORCE_MODE:
            return settings.MINERU_FORCE_MODE
        
        # 基于环境和时间的智能选择
        environment = settings.ENVIRONMENT.lower()
        current_hour = datetime.now().hour
        
        # 解析夜间时间范围
        night_hours = settings.MINERU_NIGHTTIME_HOURS.split("-")
        if len(night_hours) == 2:
            night_start = int(night_hours[0])
            night_end = int(night_hours[1])
            is_nighttime = (
                (night_start > night_end and (current_hour >= night_start or current_hour < night_end)) or
                (night_start < night_end and night_start <= current_hour < night_end)
            )
        else:
            is_nighttime = False
        
        # 策略选择逻辑
        if environment == "production" and is_nighttime:
            return "sglang"  # 生产环境夜间使用远程SGLang
        elif environment == "production":
            return "fallback"  # 生产环境白天使用降级方案
        elif environment == "development":
            return "sglang" if settings.MINERU_SGLANG_SERVER_URL else "fallback"
        else:
            return "fallback"  # 默认降级方案
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, bool]:
        """验证配置项"""
        validations = {
            "sglang_server_configured": bool(settings.MINERU_SGLANG_SERVER_URL),
            "environment_set": bool(settings.ENVIRONMENT),
            "nighttime_hours_valid": cls._validate_nighttime_hours(),
            "pdf_preprocessing_available": PDF_PREPROCESSING_AVAILABLE
        }
        
        return validations
    
    @classmethod
    def _validate_nighttime_hours(cls) -> bool:
        """验证夜间时间配置"""
        try:
            hours = settings.MINERU_NIGHTTIME_HOURS.split("-")
            if len(hours) != 2:
                return False
            start, end = int(hours[0]), int(hours[1])
            return 0 <= start <= 23 and 0 <= end <= 23
        except:
            return False


class MinerUErrorHandler:
    """MinerU错误处理类"""
    
    def __init__(self):
        self.error_counts = {}
        self.performance_metrics = {}
    
    async def with_retry(self, func, filename: str, max_retries: int = 3, *args, **kwargs):
        """统一重试逻辑"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                result = await func(*args, **kwargs)
                if result:
                    return result
                else:
                    logger.warning(f"尝试 {attempt + 1}/{max_retries} 失败: {filename} (结果为空)")
            except Exception as e:
                last_exception = e
                logger.warning(f"尝试 {attempt + 1}/{max_retries} 失败: {filename} - {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
        
        # 记录最终失败
        self._record_error(filename, last_exception or Exception("处理失败"))
        return None
    
    def _record_error(self, filename: str, error: Exception):
        """记录错误信息"""
        error_type = type(error).__name__
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        logger.error(f"处理失败记录: {filename} - {error_type}: {error}")
    
    def log_processing_metrics(self, filename: str, strategy: str, duration: float, success: bool):
        """记录处理指标"""
        if strategy not in self.performance_metrics:
            self.performance_metrics[strategy] = {
                "success_count": 0,
                "failure_count": 0,
                "total_time": 0.0,
                "files_processed": []
            }
        
        metrics = self.performance_metrics[strategy]
        if success:
            metrics["success_count"] += 1
            metrics["total_time"] += duration
        else:
            metrics["failure_count"] += 1
        
        metrics["files_processed"].append({
            "filename": filename,
            "duration": duration,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保留最近100个处理记录
        if len(metrics["files_processed"]) > 100:
            metrics["files_processed"] = metrics["files_processed"][-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        summary = {}
        for strategy, metrics in self.performance_metrics.items():
            total = metrics["success_count"] + metrics["failure_count"]
            avg_time = metrics["total_time"] / metrics["success_count"] if metrics["success_count"] > 0 else 0
            
            summary[strategy] = {
                "success_rate": metrics["success_count"] / total if total > 0 else 0,
                "average_processing_time": avg_time,
                "total_processed": total
            }
        
        return summary


class UnifiedMinerUProcessor:
    """统一MinerU处理器"""
    
    def __init__(self):
        """初始化处理器"""
        self.strategies = {
            'sglang': SGLangStrategy(),
            'vlm': VLMStrategy(),
            'pipeline': PipelineStrategy(),
            'fallback': FallbackStrategy()
        }
        
        self.config = MinerUConfig()
        self.error_handler = MinerUErrorHandler()
        
        # 验证配置
        config_validation = self.config.validate_configuration()
        logger.info(f"MinerU配置验证结果: {config_validation}")
        
        # 报告配置状态
        self._report_configuration_status()
    
    def _report_configuration_status(self):
        """报告配置状态"""
        strategy = self.config.get_processing_strategy()
        logger.info(f"UnifiedMinerUProcessor已初始化")
        logger.info(f"选定处理策略: {strategy}")
        logger.info(f"环境: {settings.ENVIRONMENT}")
        logger.info(f"夜间时间: {settings.MINERU_NIGHTTIME_HOURS}")
        
        if strategy == "sglang" and settings.MINERU_SGLANG_SERVER_URL:
            logger.info(f"SGLang服务器: {settings.MINERU_SGLANG_SERVER_URL}")
        elif strategy == "sglang":
            logger.warning("选择了SGLang策略但未配置服务器URL，将自动降级")
    
    async def process_document_bytes(self, file_bytes: bytes, filename: str, strategy: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        统一文档处理入口
        
        Args:
            file_bytes: 文件字节数据
            filename: 文件名
            strategy: 指定处理策略（可选，默认智能选择）
        
        Returns:
            处理结果或None
        """
        if not file_bytes:
            logger.error(f"文件数据为空: {filename}")
            return None
        
        # 选择处理策略
        selected_strategy = strategy or self.config.get_processing_strategy()
        
        # PDF预处理
        if filename.lower().endswith('.pdf') and PDF_PREPROCESSING_AVAILABLE:
            try:
                logger.debug(f"应用PDF预处理: {filename}")
                file_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(file_bytes)
            except Exception as e:
                logger.warning(f"PDF预处理失败，使用原始数据: {filename} - {e}")
        
        file_size_mb = len(file_bytes) / 1024 / 1024
        logger.info(f"开始处理: {filename} ({file_size_mb:.2f} MB) - 策略: {selected_strategy}")
        
        start_time = time.time()
        
        # 尝试主要策略
        result = await self._try_strategy(selected_strategy, file_bytes, filename)
        
        # 如果主要策略失败，尝试降级策略
        if not result and selected_strategy != "fallback":
            logger.warning(f"主策略 {selected_strategy} 失败，尝试降级策略")
            result = await self._try_strategy("fallback", file_bytes, filename)
        
        # 记录处理指标
        processing_time = time.time() - start_time
        success = result is not None
        self.error_handler.log_processing_metrics(filename, selected_strategy, processing_time, success)
        
        if result:
            logger.info(f"处理成功: {filename} (耗时: {processing_time:.2f}s)")
        else:
            logger.error(f"所有策略都失败: {filename}")
        
        return result
    
    async def _try_strategy(self, strategy_name: str, file_bytes: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """尝试指定策略"""
        if strategy_name not in self.strategies:
            logger.error(f"未知处理策略: {strategy_name}")
            return None
        
        strategy = self.strategies[strategy_name]
        
        # 使用错误处理器进行重试
        result = await self.error_handler.with_retry(
            strategy.process,
            filename,
            max_retries=3,
            file_bytes=file_bytes,
            filename=filename
        )
        
        return result
    
    def get_strategy_statistics(self) -> Dict[str, Dict[str, Any]]:
        """获取策略统计信息"""
        stats = {}
        for name, strategy in self.strategies.items():
            stats[name] = {
                "success_count": strategy.success_count,
                "failure_count": strategy.failure_count,
                "success_rate": strategy.get_success_rate(),
                "average_processing_time": strategy.get_average_processing_time()
            }
        
        return stats
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        return {
            "strategy_stats": self.get_strategy_statistics(),
            "error_handler_metrics": self.error_handler.get_performance_summary(),
            "configuration": self.config.validate_configuration()
        }


# 全局处理器实例
_unified_processor = None

def get_unified_mineru_processor() -> UnifiedMinerUProcessor:
    """获取统一MinerU处理器实例（单例模式）"""
    global _unified_processor
    
    if _unified_processor is None:
        _unified_processor = UnifiedMinerUProcessor()
    
    return _unified_processor


# 向后兼容的工厂函数
def get_mineru_processor():
    """向后兼容：返回统一处理器"""
    return get_unified_mineru_processor()


# 导出接口
__all__ = [
    "UnifiedMinerUProcessor",
    "get_unified_mineru_processor", 
    "get_mineru_processor",
    "MinerUConfig",
    "MinerUErrorHandler"
]