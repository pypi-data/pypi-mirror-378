"""
Обработчик для ZeroDivisionError
ZeroDivisionError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class ZeroDivisionErrorHandler(BaseHandler):
    """Обработчик для ZeroDivisionError - ошибок деления на ноль
    Handler for ZeroDivisionError - division by zero errors"""
    
    def explain(self, exception: ZeroDivisionError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет ZeroDivisionError простыми словами
        Explains ZeroDivisionError in simple terms
        
        Args:
            exception: ZeroDivisionError для объяснения / ZeroDivisionError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        # Получаем контекстную информацию
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        if self._get_language() == "ru":
            explanation = "🚫 Деление на ноль невозможно"
        else:
            explanation = "🚫 Division by zero is not allowed"
        
        # Анализируем контекст для более детального объяснения
        division_info = self._analyze_division_context(locals_dict)
        if division_info:
            if self._get_language() == "ru":
                explanation += f"\n📊 Вы пытались разделить {division_info['dividend']} на {division_info['divisor']}"
            else:
                explanation += f"\n📊 You tried to divide {division_info['dividend']} by {division_info['divisor']}"
        
        # Добавляем математическое объяснение
        if self._get_language() == "ru":
            explanation += "\n🧮 В математике деление на ноль не определено"
        else:
            explanation += "\n🧮 In mathematics, division by zero is undefined"
        
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
    
    def _analyze_division_context(self, locals_dict: dict) -> Optional[dict]:
        """Анализирует контекст деления / Analyzes division context"""
        # Ищем переменные, которые могут быть связаны с делением
        for var_name, var_value in locals_dict.items():
            if isinstance(var_value, (int, float)) and var_value == 0:
                # Ищем переменную-делимое
                for other_var_name, other_var_value in locals_dict.items():
                    if (other_var_name != var_name and 
                        isinstance(other_var_value, (int, float)) and 
                        other_var_value != 0):
                        return {
                            'dividend': f"{other_var_name} ({other_var_value})",
                            'divisor': f"{var_name} ({var_value})"
                        }
        
        return None
    
    def get_suggestions(self, exception: ZeroDivisionError) -> list[str]:
        """Возвращает предложения по исправлению ZeroDivisionError / Returns suggestions for fixing ZeroDivisionError"""
        if self._get_language() == "ru":
            return [
                "Проверьте, что делитель не равен нулю перед делением",
                "Используйте условную проверку: if divisor != 0: result = dividend / divisor",
                "Обработайте исключение: try-except ZeroDivisionError",
                "Используйте math.isclose() для проверки на ноль с учетом погрешности",
                "Проверьте входные данные на корректность",
                "Используйте безопасное деление: dividend / divisor if divisor != 0 else 0"
            ]
        else:
            return [
                "Check that the divisor is not zero before dividing",
                "Use conditional check: if divisor != 0: result = dividend / divisor",
                "Handle the exception: try-except ZeroDivisionError",
                "Use math.isclose() to check for zero with tolerance",
                "Validate input data for correctness",
                "Use safe division: dividend / divisor if divisor != 0 else 0"
            ]