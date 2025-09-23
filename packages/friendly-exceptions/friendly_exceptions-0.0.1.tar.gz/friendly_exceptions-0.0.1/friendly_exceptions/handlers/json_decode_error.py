"""
Обработчик для JSONDecodeError
JSONDecodeError handler
"""

import json
from typing import Optional, Any
from .base import BaseHandler


class JSONDecodeErrorHandler(BaseHandler):
    """Обработчик для JSONDecodeError - ошибок декодирования JSON
    Handler for JSONDecodeError - JSON decoding errors"""
    
    def explain(self, exception: json.JSONDecodeError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет JSONDecodeError простыми словами
        Explains JSONDecodeError in simple terms
        
        Args:
            exception: JSONDecodeError для объяснения / JSONDecodeError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"📄 Ошибка декодирования JSON: {error_message}"
        else:
            explanation = f"📄 JSON decoding error: {error_message}"
        
        # Извлекаем информацию о позиции ошибки
        if hasattr(exception, 'pos'):
            pos = exception.pos
            if self._get_language() == "ru":
                explanation += f"\n📍 Позиция ошибки: символ {pos}"
            else:
                explanation += f"\n📍 Error position: character {pos}"
        
        if hasattr(exception, 'lineno'):
            lineno = exception.lineno
            if self._get_language() == "ru":
                explanation += f"\n📏 Строка: {lineno}"
            else:
                explanation += f"\n📏 Line: {lineno}"
        
        if hasattr(exception, 'colno'):
            colno = exception.colno
            if self._get_language() == "ru":
                explanation += f"\n📐 Столбец: {colno}"
            else:
                explanation += f"\n📐 Column: {colno}"
        
        # Анализируем тип ошибки
        if "Expecting" in error_message:
            explanation = self._explain_expecting_error(error_message)
        elif "Invalid" in error_message:
            explanation = self._explain_invalid_error(error_message)
        elif "Unterminated" in error_message:
            explanation = self._explain_unterminated_error(error_message)
        elif "Extra data" in error_message:
            explanation = self._explain_extra_data_error(error_message)
        
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
    
    def _explain_expecting_error(self, error_message: str) -> str:
        """Объясняет ошибку 'ожидается' / Explains 'expecting' error"""
        if self._get_language() == "ru":
            return "🔍 JSON содержит синтаксическую ошибку. Ожидается другой символ"
        else:
            return "🔍 JSON contains a syntax error. A different character is expected"
    
    def _explain_invalid_error(self, error_message: str) -> str:
        """Объясняет ошибку 'неверный' / Explains 'invalid' error"""
        if self._get_language() == "ru":
            return "❌ JSON содержит неверный символ или структуру"
        else:
            return "❌ JSON contains an invalid character or structure"
    
    def _explain_unterminated_error(self, error_message: str) -> str:
        """Объясняет ошибку 'незавершенный' / Explains 'unterminated' error"""
        if self._get_language() == "ru":
            return "🔚 JSON содержит незавершенную структуру (отсутствует закрывающая скобка или кавычка)"
        else:
            return "🔚 JSON contains an unterminated structure (missing closing bracket or quote)"
    
    def _explain_extra_data_error(self, error_message: str) -> str:
        """Объясняет ошибку 'лишние данные' / Explains 'extra data' error"""
        if self._get_language() == "ru":
            return "➕ JSON содержит лишние данные после завершения объекта"
        else:
            return "➕ JSON contains extra data after the end of the object"
    
    def get_suggestions(self, exception: json.JSONDecodeError) -> list[str]:
        """Возвращает предложения по исправлению JSONDecodeError / Returns suggestions for fixing JSONDecodeError"""
        if self._get_language() == "ru":
            return [
                "Проверьте синтаксис JSON на валидность",
                "Убедитесь, что все скобки и кавычки закрыты",
                "Проверьте, что нет лишних запятых",
                "Используйте JSON валидатор для проверки",
                "Проверьте кодировку файла (должна быть UTF-8)",
                "Убедитесь, что данные действительно в формате JSON"
            ]
        else:
            return [
                "Check JSON syntax for validity",
                "Make sure all brackets and quotes are closed",
                "Check for extra commas",
                "Use a JSON validator to check",
                "Check file encoding (should be UTF-8)",
                "Make sure the data is actually in JSON format"
            ]
