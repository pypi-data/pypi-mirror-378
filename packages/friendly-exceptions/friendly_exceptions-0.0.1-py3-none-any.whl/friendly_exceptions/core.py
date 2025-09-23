"""
Основной модуль для перехвата и обработки исключений
Core module for intercepting and handling exceptions
"""

import sys
import traceback
import time
from typing import Optional, Dict, Any
from .handlers import BaseHandler, get_handler_for_exception
from .config import get_config, set_config, get_config_value
from .logging import setup_logging, get_logger, log_exception, log_handler_performance, log_language_switch

# Инициализируем логирование
setup_logging()
logger = get_logger()

# Глобальная переменная для языка
_CURRENT_LANGUAGE = "ru"


class FriendlyException(Exception):
    """Исключение с человеко-читаемым сообщением"""
    
    def __init__(self, original_exception: Exception, friendly_message: str):
        self.original_exception = original_exception
        self.friendly_message = friendly_message
        super().__init__(friendly_message)


def explain() -> None:
    """
    Перехватывает последнее исключение и выводит его в человеко-читаемом виде
    Intercepts the last exception and displays it in human-readable format
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    if exc_type is None:
        if _CURRENT_LANGUAGE == "ru":
            print("❌ Нет активных исключений для объяснения")
        else:
            print("❌ No active exceptions to explain")
        return
    
    # Получаем обработчик для данного типа исключения
    handler = get_handler_for_exception(exc_type)
    
    if handler:
        try:
            friendly_message = handler.explain(exc_value, exc_traceback)
            print(f"🔍 {friendly_message}")
            
            # Показываем оригинальную трассировку для отладки
            if _CURRENT_LANGUAGE == "ru":
                print("\n📋 Оригинальная ошибка:")
            else:
                print("\n📋 Original error:")
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            
        except Exception as e:
            if _CURRENT_LANGUAGE == "ru":
                print(f"❌ Ошибка при обработке исключения: {e}")
            else:
                print(f"❌ Error processing exception: {e}")
            traceback.print_exception(exc_type, exc_value, exc_traceback)
    else:
        if _CURRENT_LANGUAGE == "ru":
            print(f"❓ Неизвестный тип исключения: {exc_type.__name__}")
            print(f"💬 Сообщение: {exc_value}")
        else:
            print(f"❓ Unknown exception type: {exc_type.__name__}")
            print(f"💬 Message: {exc_value}")
        traceback.print_exception(exc_type, exc_value, exc_traceback)


def explain_exception(exception: Exception) -> str:
    """
    Объясняет переданное исключение и возвращает человеко-читаемое сообщение
    Explains the given exception and returns a human-readable message
    
    Args:
        exception: Исключение для объяснения / Exception to explain
        
    Returns:
        Человеко-читаемое сообщение об ошибке / Human-readable error message
    """
    handler = get_handler_for_exception(type(exception))
    
    if handler:
        return handler.explain(exception, None)
    else:
        if _CURRENT_LANGUAGE == "ru":
            return f"❓ Неизвестная ошибка: {type(exception).__name__}: {exception}"
        else:
            return f"❓ Unknown error: {type(exception).__name__}: {exception}"


def _setup_global_handler() -> None:
    """
    Автоматически устанавливает глобальный обработчик исключений при импорте
    Automatically sets up global exception handler on import
    """
    def friendly_excepthook(exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            # Логируем исключение
            log_exception(exc_value)
            
            # Показываем обычный traceback, если включено в конфигурации
            if get_config_value("show_original_traceback", True):
                traceback.print_exception(exc_type, exc_value, exc_traceback)
            
            # Затем добавляем человеческое объяснение
            handler = get_handler_for_exception(exc_type)
            if handler:
                try:
                    start_time = time.time()
                    friendly_message = handler.explain(exc_value, exc_traceback)
                    execution_time = time.time() - start_time
                    
                    # Логируем производительность обработчика
                    log_handler_performance(handler.__class__.__name__, execution_time)
                    
                    if _CURRENT_LANGUAGE == "ru":
                        print(f"\n💡 Пояснение: {friendly_message}")
                    else:
                        print(f"\n💡 Explanation: {friendly_message}")
                except Exception as e:
                    logger.error(f"Error in handler {handler.__class__.__name__}: {e}")
                    if _CURRENT_LANGUAGE == "ru":
                        print(f"\n❌ Ошибка при создании пояснения: {e}")
                    else:
                        print(f"\n❌ Error creating explanation: {e}")
            else:
                logger.warning(f"No handler found for exception type: {exc_type.__name__}")
                if _CURRENT_LANGUAGE == "ru":
                    print(f"\n❓ Неизвестный тип исключения: {exc_type.__name__}")
                else:
                    print(f"\n❓ Unknown exception type: {exc_type.__name__}")
    
    # Сохраняем оригинальный excepthook для возможности восстановления
    _original_excepthook = sys.excepthook
    sys.excepthook = friendly_excepthook


def set_global_handler() -> None:
    """
    Устанавливает глобальный обработчик исключений (для совместимости)
    Sets up global exception handler (for compatibility)
    """
    _setup_global_handler()


def set_language(language: str) -> None:
    """
    Устанавливает язык для сообщений об ошибках
    Sets the language for error messages
    
    Args:
        language: Язык ('ru' или 'en') / Language ('ru' or 'en')
    """
    global _CURRENT_LANGUAGE
    
    if language.lower() in ['ru', 'en']:
        old_language = _CURRENT_LANGUAGE
        _CURRENT_LANGUAGE = language.lower()
        
        # Обновляем конфигурацию
        set_config("language", _CURRENT_LANGUAGE)
        
        # Логируем переключение
        log_language_switch(old_language, _CURRENT_LANGUAGE)
        
        if language.lower() == "ru":
            print("🇷🇺 Язык установлен: Русский")
        else:
            print("🇺🇸 Language set: English")
    else:
        if _CURRENT_LANGUAGE == "ru":
            print("❌ Поддерживаемые языки: 'ru', 'en'")
        else:
            print("❌ Supported languages: 'ru', 'en'")


def get_language() -> str:
    """
    Возвращает текущий язык
    Returns current language
    
    Returns:
        Текущий язык / Current language
    """
    return _CURRENT_LANGUAGE
