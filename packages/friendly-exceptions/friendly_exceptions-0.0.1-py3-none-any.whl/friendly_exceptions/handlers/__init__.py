"""
Обработчики для различных типов исключений
Exception handlers for various types
"""

import json
from .base import BaseHandler
from .key_error import KeyErrorHandler
from .value_error import ValueErrorHandler
from .type_error import TypeErrorHandler
from .attribute_error import AttributeErrorHandler
from .index_error import IndexErrorHandler
from .file_not_found_error import FileNotFoundErrorHandler
from .import_error import ImportErrorHandler
from .zero_division_error import ZeroDivisionErrorHandler
from .os_error import OSErrorHandler
from .permission_error import PermissionErrorHandler
from .is_a_directory_error import IsADirectoryErrorHandler
from .connection_error import ConnectionErrorHandler
from .timeout_error import TimeoutErrorHandler
from .json_decode_error import JSONDecodeErrorHandler
from .unicode_error import UnicodeErrorHandler
from .overflow_error import OverflowErrorHandler
from .recursion_error import RecursionErrorHandler
from .memory_error import MemoryErrorHandler
from .syntax_error import SyntaxErrorHandler
from .indentation_error import IndentationErrorHandler
from .name_error import NameErrorHandler
from .assertion_error import AssertionErrorHandler
from .runtime_error import RuntimeErrorHandler
from .not_implemented_error import NotImplementedErrorHandler
from .system_error import SystemErrorHandler

# Реестр обработчиков
# Handler registry
HANDLERS = {
    # Основные исключения
    # Basic exceptions
    KeyError: KeyErrorHandler(),
    ValueError: ValueErrorHandler(),
    TypeError: TypeErrorHandler(),
    AttributeError: AttributeErrorHandler(),
    IndexError: IndexErrorHandler(),
    FileNotFoundError: FileNotFoundErrorHandler(),
    ImportError: ImportErrorHandler(),
    ModuleNotFoundError: ImportErrorHandler(),  # ModuleNotFoundError наследуется от ImportError
    ZeroDivisionError: ZeroDivisionErrorHandler(),
    NameError: NameErrorHandler(),
    AssertionError: AssertionErrorHandler(),
    
    # Синтаксические исключения
    # Syntax exceptions
    SyntaxError: SyntaxErrorHandler(),
    IndentationError: IndentationErrorHandler(),
    TabError: IndentationErrorHandler(),  # TabError наследуется от IndentationError
    
    # Системные исключения
    # System exceptions
    OSError: OSErrorHandler(),
    PermissionError: PermissionErrorHandler(),
    IsADirectoryError: IsADirectoryErrorHandler(),
    SystemError: SystemErrorHandler(),
    RuntimeError: RuntimeErrorHandler(),
    NotImplementedError: NotImplementedErrorHandler(),
    
    # Сетевые исключения
    # Network exceptions
    ConnectionError: ConnectionErrorHandler(),
    TimeoutError: TimeoutErrorHandler(),
    
    # Исключения данных
    # Data exceptions
    json.JSONDecodeError: JSONDecodeErrorHandler(),
    UnicodeError: UnicodeErrorHandler(),
    
    # Математические исключения
    # Mathematical exceptions
    OverflowError: OverflowErrorHandler(),
    
    # Исключения памяти и рекурсии
    # Memory and recursion exceptions
    RecursionError: RecursionErrorHandler(),
    MemoryError: MemoryErrorHandler(),
}


def get_handler_for_exception(exception_type: type) -> BaseHandler:
    """
    Возвращает обработчик для указанного типа исключения
    
    Args:
        exception_type: Тип исключения
        
    Returns:
        Обработчик исключения или None, если не найден
    """
    return HANDLERS.get(exception_type)


__all__ = [
    "BaseHandler",
    "KeyErrorHandler",
    "ValueErrorHandler",
    "TypeErrorHandler",
    "AttributeErrorHandler",
    "IndexErrorHandler",
    "FileNotFoundErrorHandler",
    "ImportErrorHandler",
    "ZeroDivisionErrorHandler",
    "OSErrorHandler",
    "PermissionErrorHandler",
    "IsADirectoryErrorHandler",
    "ConnectionErrorHandler",
    "TimeoutErrorHandler",
    "JSONDecodeErrorHandler",
    "UnicodeErrorHandler",
    "OverflowErrorHandler",
    "RecursionErrorHandler",
    "MemoryErrorHandler",
    "SyntaxErrorHandler",
    "IndentationErrorHandler",
    "NameErrorHandler",
    "AssertionErrorHandler",
    "RuntimeErrorHandler",
    "NotImplementedErrorHandler",
    "SystemErrorHandler",
    "get_handler_for_exception"
]
