"""
Обработчик для UnicodeError
UnicodeError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class UnicodeErrorHandler(BaseHandler):
    """Обработчик для UnicodeError - ошибок кодировки Unicode
    Handler for UnicodeError - Unicode encoding errors"""
    
    def explain(self, exception: UnicodeError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет UnicodeError простыми словами
        Explains UnicodeError in simple terms
        
        Args:
            exception: UnicodeError для объяснения / UnicodeError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"🔤 Ошибка кодировки Unicode: {error_message}"
        else:
            explanation = f"🔤 Unicode encoding error: {error_message}"
        
        # Анализируем тип ошибки
        if "UnicodeDecodeError" in str(type(exception)):
            explanation = self._explain_decode_error(exception)
        elif "UnicodeEncodeError" in str(type(exception)):
            explanation = self._explain_encode_error(exception)
        elif "UnicodeTranslateError" in str(type(exception)):
            explanation = self._explain_translate_error(exception)
        
        # Добавляем информацию о позиции
        if hasattr(exception, 'start') and hasattr(exception, 'end'):
            start, end = exception.start, exception.end
            if self._get_language() == "ru":
                explanation += f"\n📍 Позиция ошибки: символы {start}-{end}"
            else:
                explanation += f"\n📍 Error position: characters {start}-{end}"
        
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
    
    def _explain_decode_error(self, exception: UnicodeError) -> str:
        """Объясняет ошибку декодирования / Explains decode error"""
        if self._get_language() == "ru":
            return "📥 Ошибка декодирования: не удалось преобразовать байты в текст Unicode"
        else:
            return "📥 Decode error: could not convert bytes to Unicode text"
    
    def _explain_encode_error(self, exception: UnicodeError) -> str:
        """Объясняет ошибку кодирования / Explains encode error"""
        if self._get_language() == "ru":
            return "📤 Ошибка кодирования: не удалось преобразовать текст Unicode в байты"
        else:
            return "📤 Encode error: could not convert Unicode text to bytes"
    
    def _explain_translate_error(self, exception: UnicodeError) -> str:
        """Объясняет ошибку трансляции / Explains translate error"""
        if self._get_language() == "ru":
            return "🔄 Ошибка трансляции: не удалось преобразовать символы Unicode"
        else:
            return "🔄 Translate error: could not convert Unicode characters"
    
    def get_suggestions(self, exception: UnicodeError) -> list[str]:
        """Возвращает предложения по исправлению UnicodeError / Returns suggestions for fixing UnicodeError"""
        if "UnicodeDecodeError" in str(type(exception)):
            if self._get_language() == "ru":
                return [
                    "Укажите правильную кодировку при открытии файла: encoding='utf-8'",
                    "Используйте errors='ignore' для пропуска проблемных символов",
                    "Используйте errors='replace' для замены проблемных символов",
                    "Проверьте, что файл действительно в указанной кодировке",
                    "Попробуйте другие кодировки: 'latin-1', 'cp1251', 'iso-8859-1'"
                ]
            else:
                return [
                    "Specify the correct encoding when opening the file: encoding='utf-8'",
                    "Use errors='ignore' to skip problematic characters",
                    "Use errors='replace' to replace problematic characters",
                    "Check that the file is actually in the specified encoding",
                    "Try other encodings: 'latin-1', 'cp1251', 'iso-8859-1'"
                ]
        elif "UnicodeEncodeError" in str(type(exception)):
            if self._get_language() == "ru":
                return [
                    "Укажите правильную кодировку при записи файла: encoding='utf-8'",
                    "Используйте errors='ignore' для пропуска проблемных символов",
                    "Используйте errors='replace' для замены проблемных символов",
                    "Проверьте, что все символы поддерживаются целевой кодировкой",
                    "Рассмотрите использование UTF-8 для максимальной совместимости"
                ]
            else:
                return [
                    "Specify the correct encoding when writing the file: encoding='utf-8'",
                    "Use errors='ignore' to skip problematic characters",
                    "Use errors='replace' to replace problematic characters",
                    "Check that all characters are supported by the target encoding",
                    "Consider using UTF-8 for maximum compatibility"
                ]
        else:
            if self._get_language() == "ru":
                return [
                    "Проверьте кодировку входных данных",
                    "Убедитесь, что используется правильная кодировка",
                    "Используйте UTF-8 для максимальной совместимости",
                    "Обработайте ошибки кодировки с помощью параметра errors"
                ]
            else:
                return [
                    "Check the encoding of input data",
                    "Make sure the correct encoding is used",
                    "Use UTF-8 for maximum compatibility",
                    "Handle encoding errors with the errors parameter"
                ]
