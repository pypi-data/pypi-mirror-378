"""
Обработчик для OverflowError
OverflowError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class OverflowErrorHandler(BaseHandler):
    """Обработчик для OverflowError - ошибок переполнения
    Handler for OverflowError - overflow errors"""
    
    def explain(self, exception: OverflowError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет OverflowError простыми словами
        Explains OverflowError in simple terms
        
        Args:
            exception: OverflowError для объяснения / OverflowError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"🔢 Ошибка переполнения: {error_message}"
        else:
            explanation = f"🔢 Overflow error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем числа в контексте
        numbers_info = self._analyze_numbers_context(locals_dict)
        if numbers_info:
            if self._get_language() == "ru":
                explanation += f"\n📊 Проблемные числа: {numbers_info}"
            else:
                explanation += f"\n📊 Problematic numbers: {numbers_info}"
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Результат вычисления превышает максимально допустимое значение"
        else:
            explanation += "\n💡 The calculation result exceeds the maximum allowed value"
        
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
    
    def _analyze_numbers_context(self, locals_dict: dict) -> Optional[str]:
        """Анализирует контекст чисел / Analyzes numbers context"""
        numbers = []
        
        for var_name, var_value in locals_dict.items():
            if isinstance(var_value, (int, float)):
                # Проверяем на очень большие числа
                if abs(var_value) > 1e10:
                    numbers.append(f"{var_name}={var_value}")
        
        return ", ".join(numbers) if numbers else None
    
    def get_suggestions(self, exception: OverflowError) -> list[str]:
        """Возвращает предложения по исправлению OverflowError / Returns suggestions for fixing OverflowError"""
        if self._get_language() == "ru":
            return [
                "Используйте модуль decimal для точных вычислений с большими числами",
                "Проверьте входные данные на разумность",
                "Используйте модуль fractions для работы с дробями",
                "Рассмотрите использование numpy для работы с большими числами",
                "Добавьте проверки на переполнение перед вычислениями",
                "Используйте try-except для обработки переполнения"
            ]
        else:
            return [
                "Use the decimal module for precise calculations with large numbers",
                "Check input data for reasonableness",
                "Use the fractions module for working with fractions",
                "Consider using numpy for working with large numbers",
                "Add overflow checks before calculations",
                "Use try-except to handle overflow"
            ]
