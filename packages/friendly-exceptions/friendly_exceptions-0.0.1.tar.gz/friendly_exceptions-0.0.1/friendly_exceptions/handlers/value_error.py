"""
Обработчик для ValueError
ValueError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class ValueErrorHandler(BaseHandler):
    """Обработчик для ValueError - ошибок значений
    Handler for ValueError - value errors"""
    
    def explain(self, exception: ValueError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет ValueError простыми словами
        Explains ValueError in simple terms
        
        Args:
            exception: ValueError для объяснения / ValueError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        # Получаем контекстную информацию
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        if self._get_language() == "ru":
            explanation = f"⚠️ Ошибка значения: {error_message}"
        else:
            explanation = f"⚠️ Value error: {error_message}"
        
        # Анализируем сообщение об ошибке для более конкретных объяснений
        if "invalid literal" in error_message:
            explanation = self._explain_invalid_literal(error_message, locals_dict)
        elif "could not convert" in error_message:
            explanation = self._explain_conversion_error(error_message, locals_dict)
        elif "invalid format" in error_message:
            explanation = self._explain_format_error(error_message, locals_dict)
        elif "not enough values" in error_message:
            explanation = self._explain_unpacking_error(error_message, locals_dict)
        elif "too many values" in error_message:
            explanation = self._explain_unpacking_error(error_message, locals_dict)
        
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
    
    def _explain_invalid_literal(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки неверного литерала / Explains invalid literal errors"""
        if self._get_language() == "ru":
            return "🔢 Не удалось преобразовать строку в число. Проверьте формат числа."
        else:
            return "🔢 Could not convert string to number. Check the number format."
    
    def _explain_conversion_error(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки преобразования / Explains conversion errors"""
        if self._get_language() == "ru":
            return "🔄 Ошибка преобразования типа. Убедитесь, что значение можно преобразовать в нужный тип."
        else:
            return "🔄 Type conversion error. Make sure the value can be converted to the target type."
    
    def _explain_format_error(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки формата / Explains format errors"""
        if self._get_language() == "ru":
            return "📝 Неверный формат строки. Проверьте синтаксис форматирования."
        else:
            return "📝 Invalid string format. Check the formatting syntax."
    
    def _explain_unpacking_error(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки распаковки / Explains unpacking errors"""
        if self._get_language() == "ru":
            return "📦 Ошибка распаковки. Количество переменных не соответствует количеству значений."
        else:
            return "📦 Unpacking error. Number of variables doesn't match number of values."
    
    def get_suggestions(self, exception: ValueError) -> list[str]:
        """Возвращает предложения по исправлению ValueError / Returns suggestions for fixing ValueError"""
        error_message = str(exception)
        
        if "invalid literal" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте, что строка содержит только цифры и точку",
                    "Убедитесь, что нет лишних пробелов или символов",
                    "Для десятичных чисел используйте точку, а не запятую",
                    "Используйте int() для целых чисел, float() для десятичных"
                ]
            else:
                return [
                    "Check that the string contains only digits and a dot",
                    "Make sure there are no extra spaces or characters",
                    "For decimal numbers use a dot, not a comma",
                    "Use int() for integers, float() for decimals"
                ]
        elif "could not convert" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте, что значение можно преобразовать в нужный тип",
                    "Используйте isinstance() для проверки типа перед преобразованием",
                    "Обработайте исключение с помощью try-except",
                    "Проверьте документацию по функции преобразования"
                ]
            else:
                return [
                    "Check that the value can be converted to the target type",
                    "Use isinstance() to check type before conversion",
                    "Handle the exception with try-except",
                    "Check the conversion function documentation"
                ]
        elif "invalid format" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте синтаксис форматирования строки",
                    "Убедитесь, что количество плейсхолдеров соответствует аргументам",
                    "Используйте f-строки для простого форматирования",
                    "Проверьте документацию по форматированию строк"
                ]
            else:
                return [
                    "Check the string formatting syntax",
                    "Make sure the number of placeholders matches the arguments",
                    "Use f-strings for simple formatting",
                    "Check string formatting documentation"
                ]
        else:
            if self._get_language() == "ru":
                return [
                    "Проверьте корректность входных данных",
                    "Убедитесь, что значение находится в допустимом диапазоне",
                    "Используйте валидацию данных перед обработкой",
                    "Проверьте документацию по используемой функции"
                ]
            else:
                return [
                    "Check the correctness of input data",
                    "Make sure the value is within the valid range",
                    "Use data validation before processing",
                    "Check the documentation for the function you're using"
                ]