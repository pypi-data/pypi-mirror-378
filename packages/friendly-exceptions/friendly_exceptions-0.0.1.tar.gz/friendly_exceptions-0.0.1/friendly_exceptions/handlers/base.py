"""
Базовый класс для обработчиков исключений
Base class for exception handlers
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
import traceback


class BaseHandler(ABC):
    """Базовый класс для всех обработчиков исключений / Base class for all exception handlers"""
    
    def __init__(self):
        # Инициализация без установки языка - будем получать его динамически
        pass
    
    def _get_language(self):
        """Получает текущий язык динамически"""
        try:
            from ..core import get_language
            return get_language()
        except ImportError:
            return "ru"  # По умолчанию русский
    
    @abstractmethod
    def explain(self, exception: Exception, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет исключение простыми словами
        Explains exception in simple terms
        
        Args:
            exception: Исключение для объяснения / Exception to explain
            traceback_obj: Объект трассировки (может быть None) / Traceback object (can be None)
            
        Returns:
            Человеко-читаемое объяснение ошибки / Human-readable error explanation
        """
        pass
    
    def get_suggestions(self, exception: Exception) -> list[str]:
        """
        Возвращает список предложений по исправлению ошибки
        
        Args:
            exception: Исключение для анализа
            
        Returns:
            Список предложений
        """
        return []
    
    def get_context_info(self, traceback_obj: Optional[Any] = None) -> dict[str, Any]:
        """
        Извлекает контекстную информацию из трассировки
        
        Args:
            traceback_obj: Объект трассировки
            
        Returns:
            Словарь с контекстной информацией
        """
        context = {}
        
        if traceback_obj:
            try:
                # Получаем информацию о последнем фрейме
                tb = traceback_obj
                while tb.tb_next:
                    tb = tb.tb_next
                
                context.update({
                    'filename': tb.tb_frame.f_code.co_filename,
                    'function_name': tb.tb_frame.f_code.co_name,
                    'line_number': tb.tb_lineno,
                    'locals': dict(tb.tb_frame.f_locals)
                })
            except Exception:
                pass
        
        return context
