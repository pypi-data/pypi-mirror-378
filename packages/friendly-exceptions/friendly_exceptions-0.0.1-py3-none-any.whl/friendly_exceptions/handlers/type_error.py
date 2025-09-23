"""
Обработчик для TypeError
TypeError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class TypeErrorHandler(BaseHandler):
    """Обработчик для TypeError - ошибок несовместимости типов
    Handler for TypeError - type incompatibility errors"""
    
    def explain(self, exception: TypeError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет TypeError простыми словами
        
        Args:
            exception: TypeError для объяснения
            traceback_obj: Объект трассировки
            
        Returns:
            Человеко-читаемое объяснение
        """
        error_message = str(exception)
        
        # Получаем контекстную информацию
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        if self._get_language() == "ru":
            explanation = f"🔧 Ошибка типа: {error_message}"
        else:
            explanation = f"🔧 Type error: {error_message}"
        
        # Анализируем сообщение об ошибке для более конкретных объяснений
        if "unsupported operand type(s)" in error_message:
            explanation = self._explain_unsupported_operand(error_message, locals_dict)
        elif "object is not callable" in error_message:
            explanation = self._explain_not_callable(error_message, locals_dict)
        elif "object is not iterable" in error_message:
            explanation = self._explain_not_iterable(error_message, locals_dict)
        elif "missing" in error_message and "required positional argument" in error_message:
            explanation = self._explain_missing_argument(error_message, locals_dict)
        elif "takes" in error_message and "positional argument" in error_message:
            explanation = self._explain_too_many_arguments(error_message, locals_dict)
        elif "unexpected keyword argument" in error_message:
            explanation = self._explain_unexpected_keyword(error_message, locals_dict)
        elif "missing" in error_message and "required keyword-only argument" in error_message:
            explanation = self._explain_missing_keyword_argument(error_message, locals_dict)
        
        # Добавляем предложения
        suggestions = self.get_suggestions(exception)
        if suggestions:
            explanation += "\n\n🔧 Как исправить:"
            for i, suggestion in enumerate(suggestions, 1):
                explanation += f"\n{i}. {suggestion}"
        
        return explanation
    
    def _explain_unsupported_operand(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки несовместимых операндов"""
        # "unsupported operand type(s) for +: 'int' and 'str'"
        if "for +:" in error_message:
            return "➕ Нельзя складывать числа и строки. Используйте str() для преобразования числа в строку"
        elif "for -:" in error_message:
            return "➖ Нельзя вычитать из строки. Проверьте типы операндов"
        elif "for *:" in error_message:
            return "✖️ Неправильное использование оператора умножения. Для строк используйте повторение, для чисел - умножение"
        elif "for /:" in error_message:
            return "➗ Нельзя делить строки. Проверьте, что оба операнда - числа"
        else:
            return "🔧 Несовместимые типы для операции. Проверьте типы операндов"
    
    def _explain_not_callable(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки вызова не-функций"""
        # "object is not callable"
        return "📞 Вы пытаетесь вызвать объект, который не является функцией. Проверьте, что используете () только с функциями"
    
    def _explain_not_iterable(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки итерации по не-итерируемым объектам"""
        # "object is not iterable"
        return "🔄 Объект не поддерживает итерацию. Используйте for только со списками, словарями, строками и другими итерируемыми объектами"
    
    def _explain_missing_argument(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки отсутствующих аргументов"""
        # "missing 1 required positional argument: 'x'"
        return "📝 Функции не хватает обязательного аргумента. Проверьте сигнатуру функции и передайте все необходимые параметры"
    
    def _explain_too_many_arguments(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки слишком большого количества аргументов"""
        # "takes 2 positional arguments but 3 were given"
        return "📝 Функция принимает меньше аргументов, чем вы передали. Проверьте количество параметров"
    
    def _explain_unexpected_keyword(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки неожиданных именованных аргументов"""
        # "unexpected keyword argument 'x'"
        return "🏷️ Функция не принимает именованный аргумент с таким именем. Проверьте правильность названия параметра"
    
    def _explain_missing_keyword_argument(self, error_message: str, locals_dict: dict) -> str:
        """Объясняет ошибки отсутствующих именованных аргументов"""
        # "missing 1 required keyword-only argument: 'x'"
        return "🏷️ Функции не хватает обязательного именованного аргумента. Передайте его явно: func(arg=value)"
    
    def get_suggestions(self, exception: TypeError) -> list[str]:
        """Возвращает предложения по исправлению TypeError / Returns suggestions for fixing TypeError"""
        error_message = str(exception)
        
        if "unsupported operand type(s)" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте типы операндов перед операцией",
                    "Используйте явное преобразование типов: str(), int(), float()",
                    "Для строк используйте + для конкатенации, * для повторения",
                    "Для чисел используйте +, -, *, / для арифметических операций"
                ]
            else:
                return [
                    "Check operand types before operation",
                    "Use explicit type conversion: str(), int(), float()",
                    "For strings use + for concatenation, * for repetition",
                    "For numbers use +, -, *, / for arithmetic operations"
                ]
        elif "object is not callable" in error_message:
            if self._get_language() == "ru":
                return [
                    "Убедитесь, что переменная содержит функцию, а не значение",
                    "Проверьте, что вы не забыли скобки при определении функции",
                    "Используйте type() для проверки типа объекта"
                ]
            else:
                return [
                    "Make sure the variable contains a function, not a value",
                    "Check that you didn't forget parentheses when defining the function",
                    "Use type() to check object type"
                ]
        elif "object is not iterable" in error_message:
            if self._get_language() == "ru":
                return [
                    "Используйте for только с итерируемыми объектами (списки, строки, словари)",
                    "Проверьте тип объекта перед итерацией",
                    "Для чисел используйте range() для создания последовательности"
                ]
            else:
                return [
                    "Use for only with iterable objects (lists, strings, dictionaries)",
                    "Check object type before iteration",
                    "For numbers use range() to create a sequence"
                ]
        elif "missing" in error_message or "takes" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте сигнатуру функции: help(function_name)",
                    "Убедитесь, что передаете правильное количество аргументов",
                    "Проверьте, что все обязательные аргументы переданы",
                    "Используйте именованные аргументы для ясности"
                ]
            else:
                return [
                    "Check function signature: help(function_name)",
                    "Make sure you're passing the correct number of arguments",
                    "Check that all required arguments are passed",
                    "Use named arguments for clarity"
                ]
        else:
            if self._get_language() == "ru":
                return [
                    "Проверьте типы всех переменных",
                    "Убедитесь, что объекты имеют нужные методы и атрибуты",
                    "Используйте isinstance() для проверки типов",
                    "Прочитайте документацию по используемым функциям"
                ]
            else:
                return [
                    "Check types of all variables",
                    "Make sure objects have the required methods and attributes",
                    "Use isinstance() to check types",
                    "Read documentation for the functions you're using"
                ]
