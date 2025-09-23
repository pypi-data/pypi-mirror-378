"""
Система логирования для friendly_exceptions
Logging system for friendly_exceptions
"""

import logging
import sys
from typing import Optional, Any
from .config import get_config


class FriendlyFormatter(logging.Formatter):
    """Кастомный форматтер для логирования / Custom formatter for logging"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        super().__init__()
    
    def format(self, record):
        # Базовый формат
        if self.use_colors:
            # Цветные логи
            color_codes = {
                'DEBUG': '\033[36m',    # Cyan
                'INFO': '\033[32m',     # Green
                'WARNING': '\033[33m',  # Yellow
                'ERROR': '\033[31m',    # Red
                'CRITICAL': '\033[35m', # Magenta
            }
            reset_code = '\033[0m'
            
            level_color = color_codes.get(record.levelname, '')
            record.levelname = f"{level_color}{record.levelname}{reset_code}"
        
        return super().format(record)


def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None):
    """Настраивает систему логирования / Sets up logging system"""
    config = get_config()
    
    # Определяем уровень логирования
    level = log_level or config.get("log_level", "INFO")
    log_file = log_file or config.get("log_file")
    enable_colors = config.get("enable_colors", True)
    
    # Создаем логгер
    logger = logging.getLogger("friendly_exceptions")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Создаем форматтер
    formatter = FriendlyFormatter(use_colors=enable_colors and not log_file)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Обработчик для файла, если указан
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except IOError:
            logger.warning(f"Could not create log file: {log_file}")
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Получает логгер / Gets logger"""
    if name:
        return logging.getLogger(f"friendly_exceptions.{name}")
    return logging.getLogger("friendly_exceptions")


def log_exception(exception: Exception, context: str = ""):
    """Логирует исключение / Logs exception"""
    logger = get_logger()
    
    if context:
        logger.error(f"Exception in {context}: {type(exception).__name__}: {exception}")
    else:
        logger.error(f"Exception: {type(exception).__name__}: {exception}")


def log_handler_performance(handler_name: str, execution_time: float):
    """Логирует производительность обработчика / Logs handler performance"""
    logger = get_logger("performance")
    logger.debug(f"Handler {handler_name} executed in {execution_time:.4f}s")


def log_language_switch(old_language: str, new_language: str):
    """Логирует переключение языка / Logs language switch"""
    logger = get_logger()
    logger.info(f"Language switched from {old_language} to {new_language}")


def log_config_change(key: str, old_value: Any, new_value: Any):
    """Логирует изменение конфигурации / Logs config change"""
    logger = get_logger("config")
    logger.debug(f"Config changed: {key} = {old_value} -> {new_value}")
