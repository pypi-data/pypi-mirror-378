"""
Обработчик для NotImplementedError
NotImplementedError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class NotImplementedErrorHandler(BaseHandler):
    """Обработчик для NotImplementedError - ошибок нереализованных методов
    Handler for NotImplementedError - unimplemented method errors"""
    
    def explain(self, exception: NotImplementedError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет NotImplementedError простыми словами
        Explains NotImplementedError in simple terms
        
        Args:
            exception: NotImplementedError для объяснения / NotImplementedError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"🚧 Ошибка нереализованного метода: {error_message}"
        else:
            explanation = f"🚧 NotImplemented error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем информацию о классе и методе
        class_info = self._find_class_info(locals_dict)
        if class_info:
            if self._get_language() == "ru":
                explanation += f"\n🏗️ Класс: {class_info}"
            else:
                explanation += f"\n🏗️ Class: {class_info}"
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Метод или функция не была реализована (заглушка)"
        else:
            explanation += "\n💡 Method or function was not implemented (stub)"
        
        # Добавляем информацию о том, что такое NotImplementedError
        if self._get_language() == "ru":
            explanation += "\n\n📝 NotImplementedError используется для обозначения методов, которые должны быть реализованы в подклассах"
        else:
            explanation += "\n\n📝 NotImplementedError is used to indicate methods that should be implemented in subclasses"
        
        # Добавляем ссылку на документацию
        if self._get_language() == "ru":
            explanation += "\n📚 Документация: https://docs.python.org/3/library/exceptions.html#NotImplementedError"
        else:
            explanation += "\n📚 Documentation: https://docs.python.org/3/library/exceptions.html#NotImplementedError"
        
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
    
    def _find_class_info(self, locals_dict: dict) -> Optional[str]:
        """Ищет информацию о классе в контексте / Finds class information in context"""
        # Ищем переменные, которые могут быть экземплярами классов
        for var_name, var_value in locals_dict.items():
            if not var_name.startswith('__'):
                if hasattr(var_value, '__class__'):
                    class_name = var_value.__class__.__name__
                    return f"{var_name} ({class_name})"
        return None
    
    def get_suggestions(self, exception: NotImplementedError) -> list[str]:
        """Возвращает предложения по исправлению NotImplementedError / Returns suggestions for fixing NotImplementedError"""
        if self._get_language() == "ru":
            return [
                "Реализуйте недостающий метод в классе",
                "Создайте подкласс и переопределите метод",
                "Используйте абстрактный базовый класс (ABC) для принудительной реализации",
                "Проверьте, что вызываете правильный метод",
                "Рассмотрите использование pass как временной заглушки",
                "Добавьте документацию к методу с описанием того, что он должен делать",
                "Используйте @abstractmethod декоратор для обязательных методов"
            ]
        else:
            return [
                "Implement the missing method in the class",
                "Create a subclass and override the method",
                "Use abstract base class (ABC) to force implementation",
                "Check that you're calling the correct method",
                "Consider using pass as a temporary stub",
                "Add documentation to the method describing what it should do",
                "Use @abstractmethod decorator for required methods"
            ]
