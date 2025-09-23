"""
Обработчик для SystemError
SystemError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class SystemErrorHandler(BaseHandler):
    """Обработчик для SystemError - внутренних ошибок системы
    Handler for SystemError - internal system errors"""
    
    def explain(self, exception: SystemError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет SystemError простыми словами
        Explains SystemError in simple terms
        
        Args:
            exception: SystemError для объяснения / SystemError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"🔧 Внутренняя ошибка системы: {error_message}"
        else:
            explanation = f"🔧 Internal system error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем информацию о состоянии системы
        system_info = self._analyze_system_state(locals_dict)
        if system_info:
            if self._get_language() == "ru":
                explanation += f"\n📊 Состояние системы: {system_info}"
            else:
                explanation += f"\n📊 System state: {system_info}"
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Произошла внутренняя ошибка интерпретатора Python"
        else:
            explanation += "\n💡 An internal Python interpreter error occurred"
        
        # Добавляем информацию о том, что такое SystemError
        if self._get_language() == "ru":
            explanation += "\n\n📝 SystemError указывает на серьезную проблему в интерпретаторе Python"
        else:
            explanation += "\n\n📝 SystemError indicates a serious problem in the Python interpreter"
        
        # Добавляем ссылку на документацию
        if self._get_language() == "ru":
            explanation += "\n📚 Документация: https://docs.python.org/3/library/exceptions.html#SystemError"
        else:
            explanation += "\n📚 Documentation: https://docs.python.org/3/library/exceptions.html#SystemError"
        
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
    
    def _analyze_system_state(self, locals_dict: dict) -> Optional[str]:
        """Анализирует состояние системы / Analyzes system state"""
        state_info = []
        
        # Ищем системные переменные
        for var_name, var_value in locals_dict.items():
            if not var_name.startswith('__'):
                if isinstance(var_value, (int, float, str, bool)):
                    state_info.append(f"{var_name}={var_value}")
                elif hasattr(var_value, '__len__'):
                    state_info.append(f"{var_name}(len={len(var_value)})")
        
        return ", ".join(state_info[:3]) if state_info else None
    
    def get_suggestions(self, exception: SystemError) -> list[str]:
        """Возвращает предложения по исправлению SystemError / Returns suggestions for fixing SystemError"""
        if self._get_language() == "ru":
            return [
                "Перезапустите интерпретатор Python",
                "Проверьте, что используете совместимую версию Python",
                "Убедитесь, что все модули установлены правильно",
                "Проверьте, что нет поврежденных файлов .pyc",
                "Попробуйте запустить код в чистом окружении",
                "Проверьте, что нет проблем с памятью",
                "Обратитесь к разработчикам Python, если ошибка повторяется"
            ]
        else:
            return [
                "Restart the Python interpreter",
                "Check that you're using a compatible Python version",
                "Make sure all modules are installed correctly",
                "Check that there are no corrupted .pyc files",
                "Try running the code in a clean environment",
                "Check that there are no memory issues",
                "Contact Python developers if the error repeats"
            ]
