"""
MinerU统一配置管理模块
简化和集中管理所有MinerU相关配置

主要功能：
1. 配置验证和规范化
2. 智能策略选择
3. 环境适配
4. 性能优化设置

作者: Assistant
日期: 2025-01-26
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """处理配置数据类"""
    strategy: str
    max_retries: int
    timeout_seconds: int
    enable_preprocessing: bool
    fallback_enabled: bool


@dataclass
class ServerConfig:
    """服务器配置数据类"""
    sglang_url: Optional[str]
    health_check_timeout: int
    connection_pool_size: int
    request_timeout: int


@dataclass
class PerformanceConfig:
    """性能配置数据类"""
    max_concurrent_jobs: int
    memory_limit_mb: int
    cache_enabled: bool
    metrics_enabled: bool


class MinerUConfigManager:
    """MinerU配置管理器"""
    
    def __init__(self):
        """初始化配置管理器"""
        self._processing_config = None
        self._server_config = None
        self._performance_config = None
        self._config_cache = {}
        self._last_validation = None
        
        # 初始化配置
        self._initialize_configs()
        
        logger.info("MinerU配置管理器初始化完成")
    
    def _initialize_configs(self):
        """初始化所有配置"""
        self._processing_config = self._build_processing_config()
        self._server_config = self._build_server_config()
        self._performance_config = self._build_performance_config()
    
    def _build_processing_config(self) -> ProcessingConfig:
        """构建处理配置"""
        return ProcessingConfig(
            strategy=self.get_optimal_strategy(),
            max_retries=getattr(settings, 'MINERU_MAX_RETRIES', 3),
            timeout_seconds=getattr(settings, 'MINERU_TIMEOUT_SECONDS', 600),
            enable_preprocessing=getattr(settings, 'MINERU_ENABLE_PREPROCESSING', True),
            fallback_enabled=getattr(settings, 'MINERU_FALLBACK_ENABLED', True)
        )
    
    def _build_server_config(self) -> ServerConfig:
        """构建服务器配置"""
        return ServerConfig(
            sglang_url=self._validate_and_normalize_url(settings.MINERU_SGLANG_SERVER_URL),
            health_check_timeout=getattr(settings, 'MINERU_HEALTH_CHECK_TIMEOUT', 10),
            connection_pool_size=getattr(settings, 'MINERU_CONNECTION_POOL_SIZE', 10),
            request_timeout=getattr(settings, 'MINERU_REQUEST_TIMEOUT', 600)
        )
    
    def _build_performance_config(self) -> PerformanceConfig:
        """构建性能配置"""
        return PerformanceConfig(
            max_concurrent_jobs=getattr(settings, 'MINERU_MAX_CONCURRENT_JOBS', 3),
            memory_limit_mb=getattr(settings, 'MINERU_MEMORY_LIMIT_MB', 2048),
            cache_enabled=getattr(settings, 'MINERU_CACHE_ENABLED', True),
            metrics_enabled=getattr(settings, 'MINERU_METRICS_ENABLED', True)
        )
    
    def get_optimal_strategy(self) -> str:
        """获取最优处理策略"""
        # 检查强制模式
        force_mode = getattr(settings, 'MINERU_FORCE_MODE', '').lower()
        if force_mode in ['sglang', 'vlm', 'pipeline', 'fallback']:
            logger.info(f"使用强制指定策略: {force_mode}")
            return force_mode
        
        # 智能策略选择
        environment = settings.ENVIRONMENT.lower()
        current_hour = datetime.now().hour
        
        # 检查夜间时间
        is_nighttime = self._is_nighttime(current_hour)
        
        # 检查服务器可用性
        sglang_available = bool(settings.MINERU_SGLANG_SERVER_URL)
        
        # 策略选择逻辑
        if environment == "production":
            if is_nighttime and sglang_available:
                strategy = "sglang"
                reason = "生产环境夜间，使用远程SGLang"
            else:
                strategy = "fallback"
                reason = "生产环境白天，使用本地降级方案"
        elif environment == "development":
            if sglang_available:
                strategy = "sglang"
                reason = "开发环境，SGLang服务器可用"
            else:
                strategy = "fallback"
                reason = "开发环境，SGLang服务器不可用"
        elif environment == "test":
            strategy = "fallback"
            reason = "测试环境，使用稳定的降级方案"
        else:
            strategy = "fallback"
            reason = "未知环境，使用默认降级方案"
        
        logger.info(f"智能策略选择: {strategy} ({reason})")
        return strategy
    
    def _is_nighttime(self, current_hour: int) -> bool:
        """判断是否为夜间时间"""
        try:
            night_hours = getattr(settings, 'MINERU_NIGHTTIME_HOURS', '22-6')
            hours = night_hours.split('-')
            
            if len(hours) != 2:
                logger.warning(f"夜间时间配置格式错误: {night_hours}，使用默认值")
                return False
            
            night_start = int(hours[0])
            night_end = int(hours[1])
            
            # 验证时间范围
            if not (0 <= night_start <= 23 and 0 <= night_end <= 23):
                logger.warning(f"夜间时间配置超出范围: {night_hours}")
                return False
            
            # 判断是否在夜间时间范围内
            if night_start > night_end:  # 跨越午夜
                return current_hour >= night_start or current_hour < night_end
            else:  # 不跨越午夜
                return night_start <= current_hour < night_end
                
        except (ValueError, AttributeError) as e:
            logger.error(f"解析夜间时间配置失败: {e}")
            return False
    
    def _validate_and_normalize_url(self, url: Optional[str]) -> Optional[str]:
        """验证和规范化URL"""
        if not url:
            return None
        
        # 基本URL格式验证
        if not url.startswith(('http://', 'https://')):
            logger.warning(f"URL缺少协议前缀，自动添加http://: {url}")
            url = f"http://{url}"
        
        # 移除尾部斜杠
        url = url.rstrip('/')
        
        return url
    
    def validate_all_configurations(self) -> Dict[str, bool]:
        """验证所有配置项"""
        validations = {}
        
        # 基本配置验证
        validations['environment_valid'] = settings.ENVIRONMENT.lower() in ['production', 'development', 'test']
        validations['nighttime_hours_valid'] = self._validate_nighttime_hours()
        
        # 服务器配置验证
        validations['sglang_url_valid'] = self._validate_sglang_url()
        
        # 处理配置验证
        validations['strategy_valid'] = self._processing_config.strategy in ['sglang', 'vlm', 'pipeline', 'fallback']
        validations['retries_valid'] = 1 <= self._processing_config.max_retries <= 10
        validations['timeout_valid'] = 30 <= self._processing_config.timeout_seconds <= 1800
        
        # 性能配置验证
        validations['concurrent_jobs_valid'] = 1 <= self._performance_config.max_concurrent_jobs <= 20
        validations['memory_limit_valid'] = 512 <= self._performance_config.memory_limit_mb <= 8192
        
        # 依赖项验证
        try:
            from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2
            validations['pdf_preprocessing_available'] = True
        except ImportError:
            validations['pdf_preprocessing_available'] = False
        
        # 缓存验证结果
        self._last_validation = validations
        
        # 记录验证结果
        failed_validations = [k for k, v in validations.items() if not v]
        if failed_validations:
            logger.warning(f"配置验证失败项目: {failed_validations}")
        else:
            logger.info("所有配置验证通过")
        
        return validations
    
    def _validate_nighttime_hours(self) -> bool:
        """验证夜间时间配置"""
        try:
            night_hours = getattr(settings, 'MINERU_NIGHTTIME_HOURS', '22-6')
            hours = night_hours.split('-')
            
            if len(hours) != 2:
                return False
            
            start, end = int(hours[0]), int(hours[1])
            return 0 <= start <= 23 and 0 <= end <= 23
            
        except (ValueError, AttributeError):
            return False
    
    def _validate_sglang_url(self) -> bool:
        """验证SGLang服务器URL"""
        url = self._server_config.sglang_url
        if not url:
            return True  # 可选配置，没有也算有效
        
        return url.startswith(('http://', 'https://')) and '://' in url
    
    def get_processing_config(self) -> ProcessingConfig:
        """获取处理配置"""
        return self._processing_config
    
    def get_server_config(self) -> ServerConfig:
        """获取服务器配置"""
        return self._server_config
    
    def get_performance_config(self) -> PerformanceConfig:
        """获取性能配置"""
        return self._performance_config
    
    def reload_configuration(self):
        """重新加载配置"""
        logger.info("重新加载MinerU配置")
        self._config_cache.clear()
        self._initialize_configs()
        self.validate_all_configurations()
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "processing": {
                "strategy": self._processing_config.strategy,
                "max_retries": self._processing_config.max_retries,
                "timeout_seconds": self._processing_config.timeout_seconds,
                "preprocessing_enabled": self._processing_config.enable_preprocessing,
                "fallback_enabled": self._processing_config.fallback_enabled
            },
            "server": {
                "sglang_configured": bool(self._server_config.sglang_url),
                "sglang_url": self._server_config.sglang_url,
                "health_check_timeout": self._server_config.health_check_timeout,
                "connection_pool_size": self._server_config.connection_pool_size
            },
            "performance": {
                "max_concurrent_jobs": self._performance_config.max_concurrent_jobs,
                "memory_limit_mb": self._performance_config.memory_limit_mb,
                "cache_enabled": self._performance_config.cache_enabled,
                "metrics_enabled": self._performance_config.metrics_enabled
            },
            "environment": {
                "environment": settings.ENVIRONMENT,
                "nighttime_hours": getattr(settings, 'MINERU_NIGHTTIME_HOURS', '22-6'),
                "force_mode": getattr(settings, 'MINERU_FORCE_MODE', ''),
                "current_hour": datetime.now().hour,
                "is_nighttime": self._is_nighttime(datetime.now().hour)
            },
            "validation": self._last_validation or {}
        }
    
    def get_strategy_for_environment(self, environment: str, hour: Optional[int] = None) -> str:
        """为特定环境和时间获取推荐策略"""
        if hour is None:
            hour = datetime.now().hour
        
        is_night = self._is_nighttime(hour)
        sglang_available = bool(self._server_config.sglang_url)
        
        env = environment.lower()
        
        if env == "production":
            return "sglang" if is_night and sglang_available else "fallback"
        elif env == "development":
            return "sglang" if sglang_available else "fallback"
        elif env == "test":
            return "fallback"
        else:
            return "fallback"


# 全局配置管理器实例
_config_manager = None

def get_mineru_config_manager() -> MinerUConfigManager:
    """获取MinerU配置管理器实例（单例模式）"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = MinerUConfigManager()
    
    return _config_manager


# 便捷函数
def get_optimal_strategy() -> str:
    """获取最优处理策略"""
    return get_mineru_config_manager().get_optimal_strategy()


def validate_mineru_configuration() -> Dict[str, bool]:
    """验证MinerU配置"""
    return get_mineru_config_manager().validate_all_configurations()


def get_mineru_configuration_summary() -> Dict[str, Any]:
    """获取MinerU配置摘要"""
    return get_mineru_config_manager().get_configuration_summary()


# 导出接口
__all__ = [
    "MinerUConfigManager",
    "ProcessingConfig",
    "ServerConfig", 
    "PerformanceConfig",
    "get_mineru_config_manager",
    "get_optimal_strategy",
    "validate_mineru_configuration",
    "get_mineru_configuration_summary"
]