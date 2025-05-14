import logging
from logging.config import dictConfig
import os
import functools
import time
import asyncio
import traceback

# 确保日志目录存在
def setup_logger():
    """设置并配置logger"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志配置
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(log_dir, "app.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "default",
                "level": "INFO",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(log_dir, "error.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "default",
                "level": "ERROR",
            },
        },
        "root": {"level": "INFO", "handlers": ["console", "file", "error_file"]},
        "loggers": {
            "app": {"level": "INFO", "handlers": ["console", "file", "error_file"], "propagate": False},
        },
    }

    # 应用日志配置
    dictConfig(logging_config)
    
    # 获取应用logger
    logger = logging.getLogger("app")
    logger.info("Logger configured successfully")
    return logger

def get_logger(name):
    """获取指定名称的logger"""
    return logging.getLogger(name)

def log_execution_time(logger=None):
    """装饰器：记录函数执行时间"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            _logger = logger or logging.getLogger(func.__module__)
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                _logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                _logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
                _logger.error(traceback.format_exc())
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            _logger = logger or logging.getLogger(func.__module__)
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                _logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                _logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {str(e)}")
                _logger.error(traceback.format_exc())
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator