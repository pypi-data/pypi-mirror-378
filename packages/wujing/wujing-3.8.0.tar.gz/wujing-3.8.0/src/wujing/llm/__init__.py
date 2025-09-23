"""大语言模型调用模块

本模块包含LLM调用、缓存、重试等功能。
"""

# 延迟导入，避免在包初始化时就加载依赖
def __getattr__(name):
    """延迟导入模块以避免依赖问题"""
    if name == "LLMService":
        from .llm_call import LLMService
        return LLMService
    elif name == "LLMConfig":
        from .config import LLMConfig
        return LLMConfig
    elif name == "LLMRequest":
        from .config import LLMRequest
        return LLMRequest
    elif name == "CacheManager":
        from .cache import CacheManager
        return CacheManager
    elif name in ("LLMCallError", "ConfigurationError", "CacheError"):
        from .exceptions import LLMCallError, ConfigurationError, CacheError
        if name == "LLMCallError":
            return LLMCallError
        elif name == "ConfigurationError":
            return ConfigurationError
        else:
            return CacheError
    elif name == "ResponseModelType":
        from .types import ResponseModelType
        return ResponseModelType
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "LLMService",
    "LLMConfig", 
    "LLMRequest",
    "CacheManager",
    "LLMCallError",
    "ConfigurationError", 
    "CacheError",
    "ResponseModelType",
]