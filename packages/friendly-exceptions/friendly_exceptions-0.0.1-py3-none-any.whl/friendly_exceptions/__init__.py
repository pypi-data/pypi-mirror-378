"""
Friendly Exceptions - библиотека для человеко-читаемых исключений
Friendly Exceptions - library for human-readable exceptions
"""

from .core import explain, explain_exception, FriendlyException, set_language, get_language
from .handlers import (
    KeyErrorHandler,
    ValueErrorHandler,
    TypeErrorHandler,
    AttributeErrorHandler,
    IndexErrorHandler,
    FileNotFoundErrorHandler,
    ImportErrorHandler,
    ZeroDivisionErrorHandler
)

# Автоматически устанавливаем глобальный обработчик при импорте
from .core import _setup_global_handler
_setup_global_handler()

__version__ = "0.0.1"
__all__ = [
    "explain",
    "explain_exception",
    "FriendlyException",
    "set_language",
    "get_language",
    "KeyErrorHandler",
    "ValueErrorHandler", 
    "TypeErrorHandler",
    "AttributeErrorHandler",
    "IndexErrorHandler",
    "FileNotFoundErrorHandler",
    "ImportErrorHandler",
    "ZeroDivisionErrorHandler"
]
