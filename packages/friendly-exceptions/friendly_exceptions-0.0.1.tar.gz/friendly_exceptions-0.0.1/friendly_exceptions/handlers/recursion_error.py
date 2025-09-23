"""
Обработчик для RecursionError
RecursionError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class RecursionErrorHandler(BaseHandler):
    """Обработчик для RecursionError - ошибок рекурсии
    Handler for RecursionError - recursion errors"""
    
    def explain(self, exception: RecursionError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет RecursionError простыми словами
        Explains RecursionError in simple terms
        
        Args:
            exception: RecursionError для объяснения / RecursionError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"🔄 Ошибка рекурсии: {error_message}"
        else:
            explanation = f"🔄 Recursion error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем рекурсивную функцию
        function_info = self._find_recursive_function(locals_dict)
        if function_info:
            if self._get_language() == "ru":
                explanation += f"\n🔍 Рекурсивная функция: {function_info}"
            else:
                explanation += f"\n🔍 Recursive function: {function_info}"
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Функция вызывает сама себя слишком много раз"
        else:
            explanation += "\n💡 The function calls itself too many times"
        
        # Добавляем информацию о стеке
        if self._get_language() == "ru":
            explanation += "\n📚 Стек вызовов переполнен (обычно ограничен ~1000 вызовов)"
        else:
            explanation += "\n📚 Call stack is overflowed (usually limited to ~1000 calls)"
        
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
    
    def _find_recursive_function(self, locals_dict: dict) -> Optional[str]:
        """Ищет рекурсивную функцию в контексте / Finds recursive function in context"""
        # Ищем функции в локальных переменных
        for var_name, var_value in locals_dict.items():
            if callable(var_value):
                return var_name
        return None
    
    def get_suggestions(self, exception: RecursionError) -> list[str]:
        """Возвращает предложения по исправлению RecursionError / Returns suggestions for fixing RecursionError"""
        if self._get_language() == "ru":
            return [
                "Добавьте базовый случай для остановки рекурсии",
                "Проверьте, что рекурсивный вызов приближает к базовому случаю",
                "Рассмотрите использование итеративного подхода вместо рекурсии",
                "Используйте sys.setrecursionlimit() для увеличения лимита (осторожно!)",
                "Добавьте счетчик глубины рекурсии для отладки",
                "Проверьте, что нет бесконечной рекурсии"
            ]
        else:
            return [
                "Add a base case to stop the recursion",
                "Check that the recursive call approaches the base case",
                "Consider using an iterative approach instead of recursion",
                "Use sys.setrecursionlimit() to increase the limit (carefully!)",
                "Add a recursion depth counter for debugging",
                "Check that there's no infinite recursion"
            ]
