"""
Обработчик для IndentationError
IndentationError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class IndentationErrorHandler(BaseHandler):
    """Обработчик для IndentationError - ошибок отступов
    Handler for IndentationError - indentation errors"""
    
    def explain(self, exception: IndentationError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет IndentationError простыми словами
        Explains IndentationError in simple terms
        
        Args:
            exception: IndentationError для объяснения / IndentationError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"📏 Ошибка отступов: {error_message}"
        else:
            explanation = f"📏 Indentation error: {error_message}"
        
        # Извлекаем информацию о позиции ошибки
        if hasattr(exception, 'lineno') and exception.lineno:
            if self._get_language() == "ru":
                explanation += f"\n📍 Строка: {exception.lineno}"
            else:
                explanation += f"\n📍 Line: {exception.lineno}"
        
        if hasattr(exception, 'text') and exception.text:
            if self._get_language() == "ru":
                explanation += f"\n📄 Проблемная строка: '{exception.text.strip()}'"
            else:
                explanation += f"\n📄 Problematic line: '{exception.text.strip()}'"
        
        # Анализируем тип ошибки отступов
        if "unexpected indent" in error_message.lower():
            explanation = self._explain_unexpected_indent(error_message)
        elif "unindent does not match" in error_message.lower():
            explanation = self._explain_unindent_mismatch(error_message)
        elif "expected an indented block" in error_message.lower():
            explanation = self._explain_expected_indented_block(error_message)
        
        # Объясняем важность отступов в Python
        if self._get_language() == "ru":
            explanation += "\n\n💡 В Python отступы определяют структуру кода (блоки if, for, while, def, class)"
        else:
            explanation += "\n\n💡 In Python, indentation defines code structure (if, for, while, def, class blocks)"
        
        # Добавляем ссылку на документацию
        if self._get_language() == "ru":
            explanation += "\n📚 Документация: https://docs.python.org/3/reference/lexical_analysis.html#indentation"
        else:
            explanation += "\n📚 Documentation: https://docs.python.org/3/reference/lexical_analysis.html#indentation"
        
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
    
    def _explain_unexpected_indent(self, error_message: str) -> str:
        """Объясняет ошибку 'неожиданный отступ' / Explains 'unexpected indent' error"""
        if self._get_language() == "ru":
            return "📏 Неожиданный отступ. Строка имеет отступ, но не должна его иметь"
        else:
            return "📏 Unexpected indent. Line has indentation but shouldn't"
    
    def _explain_unindent_mismatch(self, error_message: str) -> str:
        """Объясняет ошибку 'несоответствие отступов' / Explains 'unindent mismatch' error"""
        if self._get_language() == "ru":
            return "📐 Несоответствие отступов. Отступ не соответствует предыдущему уровню"
        else:
            return "📐 Indent mismatch. Indentation doesn't match previous level"
    
    def _explain_expected_indented_block(self, error_message: str) -> str:
        """Объясняет ошибку 'ожидается блок с отступом' / Explains 'expected indented block' error"""
        if self._get_language() == "ru":
            return "📦 Ожидается блок кода с отступом после двоеточия (:)"
        else:
            return "📦 Expected indented block after colon (:)"
    
    def get_suggestions(self, exception: IndentationError) -> list[str]:
        """Возвращает предложения по исправлению IndentationError / Returns suggestions for fixing IndentationError"""
        if self._get_language() == "ru":
            return [
                "Используйте 4 пробела для каждого уровня отступа",
                "Не смешивайте табы и пробелы - выберите один вариант",
                "Проверьте, что все строки в блоке имеют одинаковый отступ",
                "Убедитесь, что после двоеточия (:) есть отступ",
                "Используйте IDE с автоматическим форматированием кода",
                "Проверьте, что нет лишних пробелов в начале строки",
                "Используйте команду 'python -m py_compile file.py' для проверки синтаксиса"
            ]
        else:
            return [
                "Use 4 spaces for each indentation level",
                "Don't mix tabs and spaces - choose one option",
                "Check that all lines in a block have the same indentation",
                "Make sure there's indentation after colon (:)",
                "Use an IDE with automatic code formatting",
                "Check that there are no extra spaces at the beginning of the line",
                "Use 'python -m py_compile file.py' command to check syntax"
            ]
