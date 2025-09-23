"""
Обработчик для TimeoutError
TimeoutError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class TimeoutErrorHandler(BaseHandler):
    """Обработчик для TimeoutError - ошибок таймаута
    Handler for TimeoutError - timeout errors"""
    
    def explain(self, exception: TimeoutError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет TimeoutError простыми словами
        Explains TimeoutError in simple terms
        
        Args:
            exception: TimeoutError для объяснения / TimeoutError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"⏰ Ошибка таймаута: {error_message}"
        else:
            explanation = f"⏰ Timeout error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем информацию о таймауте
        timeout_info = self._analyze_timeout_context(locals_dict)
        if timeout_info:
            if self._get_language() == "ru":
                explanation += f"\n⏱️ Таймаут: {timeout_info}"
            else:
                explanation += f"\n⏱️ Timeout: {timeout_info}"
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Операция заняла слишком много времени и была прервана"
        else:
            explanation += "\n💡 The operation took too long and was interrupted"
        
        # Добавляем предложения
        suggestions = self.get_suggestions(exception)
        if suggestions:
            if self._get_language() == "ru":
                explanation += "\n\n🔧 Как исправить:"
            else:
                explanation += "\n\n🔧 How to fix:"
            for i, suggestion in enumerate(suggestions, 1):
                explanation += f"\n{i}. {suggestion}"
        
        return explanation
    
    def _analyze_timeout_context(self, locals_dict: dict) -> Optional[str]:
        """Анализирует контекст таймаута / Analyzes timeout context"""
        # Ищем переменные, связанные с таймаутом
        timeout_vars = ['timeout', 'timeout_seconds', 'timeout_ms', 'wait_time']
        
        for var_name, var_value in locals_dict.items():
            if var_name.lower() in timeout_vars:
                if isinstance(var_value, (int, float)):
                    return f"{var_value} секунд" if self._get_language() == "ru" else f"{var_value} seconds"
        
        return None
    
    def get_suggestions(self, exception: TimeoutError) -> list[str]:
        """Возвращает предложения по исправлению TimeoutError / Returns suggestions for fixing TimeoutError"""
        if self._get_language() == "ru":
            return [
                "Увеличьте значение таймаута",
                "Проверьте скорость интернет-соединения",
                "Убедитесь, что сервер работает нормально",
                "Попробуйте повторить операцию позже",
                "Проверьте, что нет проблем с сетью",
                "Рассмотрите возможность асинхронного выполнения"
            ]
        else:
            return [
                "Increase the timeout value",
                "Check your internet connection speed",
                "Make sure the server is working properly",
                "Try the operation again later",
                "Check for network issues",
                "Consider using asynchronous execution"
            ]
