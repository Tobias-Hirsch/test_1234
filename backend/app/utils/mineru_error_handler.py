"""
MinerU统一错误处理模块
提供标准化的错误处理、重试机制和性能监控

主要功能：
1. 统一错误处理和分类
2. 智能重试机制
3. 性能指标收集
4. 错误统计和分析

作者: Assistant
日期: 2025-01-26
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """错误分类"""
    NETWORK_ERROR = "network"
    TIMEOUT_ERROR = "timeout"
    AUTHENTICATION_ERROR = "auth"
    RATE_LIMIT_ERROR = "rate_limit"
    SERVER_ERROR = "server"
    CLIENT_ERROR = "client"
    PROCESSING_ERROR = "processing"
    CONFIGURATION_ERROR = "config"
    UNKNOWN_ERROR = "unknown"


@dataclass
class ErrorMetrics:
    """错误指标"""
    category: ErrorCategory
    count: int = 0
    first_occurrence: Optional[datetime] = None
    last_occurrence: Optional[datetime] = None
    total_retry_attempts: int = 0
    successful_retries: int = 0
    
    def record_error(self, retry_attempt: int = 0, retry_success: bool = False):
        """记录错误"""
        self.count += 1
        now = datetime.now()
        
        if self.first_occurrence is None:
            self.first_occurrence = now
        self.last_occurrence = now
        
        if retry_attempt > 0:
            self.total_retry_attempts += 1
            if retry_success:
                self.successful_retries += 1


@dataclass
class ProcessingMetrics:
    """处理指标"""
    strategy: str
    filename: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    success: bool = False
    error_category: Optional[ErrorCategory] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    file_size_mb: float = 0.0
    
    def mark_completed(self, success: bool, error_category: Optional[ErrorCategory] = None, error_message: Optional[str] = None):
        """标记处理完成"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.error_category = error_category
        self.error_message = error_message


class RetryStrategy:
    """重试策略"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, exponential_base: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def get_delay(self, attempt: int) -> float:
        """计算重试延迟"""
        if attempt <= 0:
            return 0.0
        
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)
    
    def should_retry(self, attempt: int, error_category: ErrorCategory) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False
        
        # 根据错误类型决定是否重试
        non_retryable_errors = {
            ErrorCategory.AUTHENTICATION_ERROR,
            ErrorCategory.CONFIGURATION_ERROR,
            ErrorCategory.CLIENT_ERROR  # 4xx错误通常不应该重试
        }
        
        return error_category not in non_retryable_errors


class MinerUErrorHandler:
    """MinerU错误处理器"""
    
    def __init__(self):
        self.error_metrics: Dict[ErrorCategory, ErrorMetrics] = {}
        self.processing_history: List[ProcessingMetrics] = []
        self.retry_strategy = RetryStrategy()
        
        # 初始化错误指标
        for category in ErrorCategory:
            self.error_metrics[category] = ErrorMetrics(category)
        
        logger.info("MinerU错误处理器初始化完成")
    
    def classify_error(self, error: Exception) -> ErrorCategory:
        """错误分类"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # 网络相关错误
        if any(keyword in error_type.lower() for keyword in ['connection', 'network', 'dns', 'socket']):
            return ErrorCategory.NETWORK_ERROR
        
        # 超时错误
        if 'timeout' in error_type.lower() or 'timeout' in error_message:
            return ErrorCategory.TIMEOUT_ERROR
        
        # HTTP状态码相关
        if hasattr(error, 'status') or hasattr(error, 'status_code'):
            status = getattr(error, 'status', None) or getattr(error, 'status_code', None)
            if status:
                if status == 401:
                    return ErrorCategory.AUTHENTICATION_ERROR
                elif status == 429:
                    return ErrorCategory.RATE_LIMIT_ERROR
                elif 500 <= status < 600:
                    return ErrorCategory.SERVER_ERROR
                elif 400 <= status < 500:
                    return ErrorCategory.CLIENT_ERROR
        
        # 认证相关
        if any(keyword in error_message for keyword in ['auth', 'unauthorized', 'forbidden', 'token']):
            return ErrorCategory.AUTHENTICATION_ERROR
        
        # 配置相关
        if any(keyword in error_message for keyword in ['config', 'setting', 'environment', 'variable']):
            return ErrorCategory.CONFIGURATION_ERROR
        
        # 处理相关
        if any(keyword in error_message for keyword in ['parse', 'process', 'convert', 'extract']):
            return ErrorCategory.PROCESSING_ERROR
        
        return ErrorCategory.UNKNOWN_ERROR
    
    async def with_retry(
        self,
        func: Callable,
        filename: str,
        strategy: str,
        file_size_mb: float = 0.0,
        *args,
        **kwargs
    ) -> Tuple[Any, ProcessingMetrics]:
        """
        使用重试机制执行函数
        
        Args:
            func: 要执行的异步函数
            filename: 文件名
            strategy: 处理策略
            file_size_mb: 文件大小(MB)
            *args, **kwargs: 传递给函数的参数
            
        Returns:
            (结果, 处理指标)
        """
        metrics = ProcessingMetrics(
            strategy=strategy,
            filename=filename,
            start_time=datetime.now(),
            file_size_mb=file_size_mb
        )
        
        last_error = None
        last_error_category = None
        
        for attempt in range(self.retry_strategy.max_retries + 1):
            try:
                # 记录重试次数
                metrics.retry_count = attempt
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                if result:
                    # 成功
                    metrics.mark_completed(True)
                    self.processing_history.append(metrics)
                    
                    # 如果之前有重试，记录成功的重试
                    if attempt > 0 and last_error_category:
                        self.error_metrics[last_error_category].record_error(attempt, True)
                    
                    logger.info(f"处理成功: {filename} (尝试: {attempt + 1}, 耗时: {metrics.duration:.2f}s)")
                    return result, metrics
                else:
                    # 结果为空，视为失败
                    error_category = ErrorCategory.PROCESSING_ERROR
                    error_message = "处理结果为空"
                    
                    if attempt < self.retry_strategy.max_retries:
                        logger.warning(f"处理结果为空，准备重试: {filename} (尝试: {attempt + 1})")
                        last_error_category = error_category
                        
                        # 等待重试
                        delay = self.retry_strategy.get_delay(attempt + 1)
                        if delay > 0:
                            await asyncio.sleep(delay)
                        continue
                    else:
                        # 最后一次尝试仍然失败
                        metrics.mark_completed(False, error_category, error_message)
                        self.error_metrics[error_category].record_error(attempt)
                        self.processing_history.append(metrics)
                        
                        logger.error(f"所有重试都失败: {filename} (最终错误: {error_message})")
                        return None, metrics
            
            except Exception as e:
                last_error = e
                error_category = self.classify_error(e)
                last_error_category = error_category
                
                # 检查是否应该重试
                if attempt < self.retry_strategy.max_retries and self.retry_strategy.should_retry(attempt, error_category):
                    logger.warning(f"处理失败，准备重试: {filename} (尝试: {attempt + 1}, 错误: {error_category.value}) - {e}")
                    
                    # 记录重试错误
                    self.error_metrics[error_category].record_error(attempt, False)
                    
                    # 等待重试
                    delay = self.retry_strategy.get_delay(attempt + 1)
                    if delay > 0:
                        await asyncio.sleep(delay)
                    continue
                else:
                    # 不重试或达到最大重试次数
                    metrics.mark_completed(False, error_category, str(e))
                    self.error_metrics[error_category].record_error(attempt)
                    self.processing_history.append(metrics)
                    
                    logger.error(f"处理最终失败: {filename} (错误: {error_category.value}) - {e}")
                    return None, metrics
        
        # 这行不应该被执行到
        return None, metrics
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计"""
        stats = {}
        
        for category, metrics in self.error_metrics.items():
            if metrics.count > 0:
                retry_success_rate = (
                    metrics.successful_retries / metrics.total_retry_attempts 
                    if metrics.total_retry_attempts > 0 else 0
                )
                
                stats[category.value] = {
                    "count": metrics.count,
                    "first_occurrence": metrics.first_occurrence.isoformat() if metrics.first_occurrence else None,
                    "last_occurrence": metrics.last_occurrence.isoformat() if metrics.last_occurrence else None,
                    "total_retry_attempts": metrics.total_retry_attempts,
                    "successful_retries": metrics.successful_retries,
                    "retry_success_rate": retry_success_rate
                }
        
        return stats
    
    def get_processing_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """获取处理统计（最近N小时）"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.processing_history if m.start_time >= cutoff_time]
        
        if not recent_metrics:
            return {"message": f"最近{hours}小时内无处理记录"}
        
        # 按策略分组统计
        strategy_stats = {}
        for metrics in recent_metrics:
            strategy = metrics.strategy
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "total_count": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "total_duration": 0.0,
                    "total_file_size_mb": 0.0,
                    "total_retries": 0
                }
            
            stats = strategy_stats[strategy]
            stats["total_count"] += 1
            stats["total_duration"] += metrics.duration
            stats["total_file_size_mb"] += metrics.file_size_mb
            stats["total_retries"] += metrics.retry_count
            
            if metrics.success:
                stats["success_count"] += 1
            else:
                stats["failure_count"] += 1
        
        # 计算汇总指标
        for strategy, stats in strategy_stats.items():
            total = stats["total_count"]
            stats["success_rate"] = stats["success_count"] / total if total > 0 else 0
            stats["average_duration"] = stats["total_duration"] / total if total > 0 else 0
            stats["average_file_size_mb"] = stats["total_file_size_mb"] / total if total > 0 else 0
            stats["average_retries"] = stats["total_retries"] / total if total > 0 else 0
        
        # 总体统计
        total_files = len(recent_metrics)
        successful_files = sum(1 for m in recent_metrics if m.success)
        
        return {
            "time_range_hours": hours,
            "total_files_processed": total_files,
            "successful_files": successful_files,
            "failed_files": total_files - successful_files,
            "overall_success_rate": successful_files / total_files if total_files > 0 else 0,
            "strategy_breakdown": strategy_stats
        }
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """获取性能洞察"""
        if not self.processing_history:
            return {"message": "暂无处理历史数据"}
        
        # 最近100个处理记录
        recent_metrics = self.processing_history[-100:]
        
        # 成功率分析
        successful = [m for m in recent_metrics if m.success]
        failed = [m for m in recent_metrics if not m.success]
        
        insights = {
            "total_samples": len(recent_metrics),
            "success_rate": len(successful) / len(recent_metrics) if recent_metrics else 0
        }
        
        if successful:
            durations = [m.duration for m in successful]
            file_sizes = [m.file_size_mb for m in successful]
            
            insights["successful_processing"] = {
                "average_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "average_file_size_mb": sum(file_sizes) / len(file_sizes) if file_sizes else 0
            }
        
        if failed:
            # 失败原因分析
            failure_categories = {}
            for m in failed:
                category = m.error_category.value if m.error_category else "unknown"
                failure_categories[category] = failure_categories.get(category, 0) + 1
            
            insights["failure_analysis"] = {
                "common_failure_categories": failure_categories,
                "average_retries_before_failure": sum(m.retry_count for m in failed) / len(failed)
            }
        
        # 策略效果分析
        strategy_performance = {}
        for m in recent_metrics:
            if m.strategy not in strategy_performance:
                strategy_performance[m.strategy] = {"total": 0, "successful": 0}
            
            strategy_performance[m.strategy]["total"] += 1
            if m.success:
                strategy_performance[m.strategy]["successful"] += 1
        
        for strategy, perf in strategy_performance.items():
            perf["success_rate"] = perf["successful"] / perf["total"] if perf["total"] > 0 else 0
        
        insights["strategy_performance"] = strategy_performance
        
        return insights
    
    def clear_old_history(self, days: int = 7):
        """清理旧的处理历史"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        old_count = len(self.processing_history)
        self.processing_history = [m for m in self.processing_history if m.start_time >= cutoff_time]
        new_count = len(self.processing_history)
        
        logger.info(f"清理了 {old_count - new_count} 条超过 {days} 天的处理历史记录")
    
    def export_metrics(self) -> Dict[str, Any]:
        """导出所有指标"""
        return {
            "error_statistics": self.get_error_statistics(),
            "processing_statistics": self.get_processing_statistics(),
            "performance_insights": self.get_performance_insights(),
            "export_timestamp": datetime.now().isoformat()
        }


# 全局错误处理器实例
_error_handler = None

def get_mineru_error_handler() -> MinerUErrorHandler:
    """获取MinerU错误处理器实例（单例模式）"""
    global _error_handler
    
    if _error_handler is None:
        _error_handler = MinerUErrorHandler()
    
    return _error_handler


# 导出接口
__all__ = [
    "MinerUErrorHandler",
    "ErrorCategory",
    "ErrorMetrics",
    "ProcessingMetrics",
    "RetryStrategy",
    "get_mineru_error_handler"
]