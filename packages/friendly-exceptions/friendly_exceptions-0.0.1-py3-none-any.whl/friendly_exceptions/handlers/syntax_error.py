"""
Обработчик для SyntaxError
SyntaxError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class SyntaxErrorHandler(BaseHandler):
    """Обработчик для SyntaxError - ошибок синтаксиса
    Handler for SyntaxError - syntax errors"""
    
    def explain(self, exception: SyntaxError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет SyntaxError простыми словами
        Explains SyntaxError in simple terms
        
        Args:
            exception: SyntaxError для объяснения / SyntaxError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"📝 Ошибка синтаксиса: {error_message}"
        else:
            explanation = f"📝 Syntax error: {error_message}"
        
        # Извлекаем информацию о позиции ошибки
        if hasattr(exception, 'lineno') and exception.lineno:
            if self._get_language() == "ru":
                explanation += f"\n📍 Строка: {exception.lineno}"
            else:
                explanation += f"\n📍 Line: {exception.lineno}"
        
        if hasattr(exception, 'offset') and exception.offset:
            if self._get_language() == "ru":
                explanation += f"\n📐 Позиция в строке: {exception.offset}"
            else:
                explanation += f"\n📐 Position in line: {exception.offset}"
        
        if hasattr(exception, 'text') and exception.text:
            if self._get_language() == "ru":
                explanation += f"\n📄 Проблемная строка: {exception.text.strip()}"
            else:
                explanation += f"\n📄 Problematic line: {exception.text.strip()}"
        
        # Анализируем тип синтаксической ошибки
        if "invalid syntax" in error_message.lower():
            explanation = self._explain_invalid_syntax(error_message)
        elif "unexpected EOF" in error_message.lower():
            explanation = self._explain_unexpected_eof(error_message)
        elif "unexpected indent" in error_message.lower():
            explanation = self._explain_unexpected_indent(error_message)
        elif "unindent does not match" in error_message.lower():
            explanation = self._explain_unindent_mismatch(error_message)
        elif "invalid character" in error_message.lower():
            explanation = self._explain_invalid_character(error_message)
        
        # Добавляем ссылку на документацию
        if self._get_language() == "ru":
            explanation += "\n\n📚 Документация: https://docs.python.org/3/reference/lexical_analysis.html"
        else:
            explanation += "\n\n📚 Documentation: https://docs.python.org/3/reference/lexical_analysis.html"
        
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
    
    def _explain_invalid_syntax(self, error_message: str) -> str:
        """Объясняет ошибку 'неверный синтаксис' / Explains 'invalid syntax' error"""
        if self._get_language() == "ru":
            return "❌ Неверный синтаксис Python. Проверьте правильность написания команд"
        else:
            return "❌ Invalid Python syntax. Check the correctness of command writing"
    
    def _explain_unexpected_eof(self, error_message: str) -> str:
        """Объясняет ошибку 'неожиданный конец файла' / Explains 'unexpected EOF' error"""
        if self._get_language() == "ru":
            return "🔚 Неожиданный конец файла. Возможно, не закрыта скобка, кавычка или блок кода"
        else:
            return "🔚 Unexpected end of file. Possibly unclosed bracket, quote, or code block"
    
    def _explain_unexpected_indent(self, error_message: str) -> str:
        """Объясняет ошибку 'неожиданный отступ' / Explains 'unexpected indent' error"""
        if self._get_language() == "ru":
            return "📏 Неожиданный отступ. Проверьте правильность отступов в коде"
        else:
            return "📏 Unexpected indent. Check the correctness of indentation in code"
    
    def _explain_unindent_mismatch(self, error_message: str) -> str:
        """Объясняет ошибку 'несоответствие отступов' / Explains 'unindent mismatch' error"""
        if self._get_language() == "ru":
            return "📐 Несоответствие отступов. Все строки в блоке должны иметь одинаковый отступ"
        else:
            return "📐 Indent mismatch. All lines in a block must have the same indentation"
    
    def _explain_invalid_character(self, error_message: str) -> str:
        """Объясняет ошибку 'неверный символ' / Explains 'invalid character' error"""
        if self._get_language() == "ru":
            return "🔤 Неверный символ в коде. Удалите или замените недопустимые символы"
        else:
            return "🔤 Invalid character in code. Remove or replace invalid characters"
    
    def get_suggestions(self, exception: SyntaxError) -> list[str]:
        """Возвращает предложения по исправлению SyntaxError / Returns suggestions for fixing SyntaxError"""
        if self._get_language() == "ru":
            return [
                "Проверьте правильность написания ключевых слов Python",
                "Убедитесь, что все скобки (), [], {} закрыты",
                "Проверьте правильность отступов (используйте 4 пробела)",
                "Убедитесь, что все строки заключены в кавычки",
                "Проверьте, что двоеточие : стоит после if, for, while, def, class",
                "Используйте IDE с подсветкой синтаксиса для проверки",
                "Проверьте, что нет смешивания табов и пробелов"
            ]
        else:
            return [
                "Check the spelling of Python keywords",
                "Make sure all brackets (), [], {} are closed",
                "Check indentation correctness (use 4 spaces)",
                "Make sure all strings are enclosed in quotes",
                "Check that colon : is after if, for, while, def, class",
                "Use an IDE with syntax highlighting for checking",
                "Check that there's no mixing of tabs and spaces"
            ]
