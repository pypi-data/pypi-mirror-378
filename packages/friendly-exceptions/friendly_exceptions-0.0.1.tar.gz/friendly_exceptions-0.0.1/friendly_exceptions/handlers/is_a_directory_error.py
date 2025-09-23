"""
Обработчик для IsADirectoryError
IsADirectoryError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class IsADirectoryErrorHandler(BaseHandler):
    """Обработчик для IsADirectoryError - ошибок работы с директориями как с файлами
    Handler for IsADirectoryError - errors treating directories as files"""
    
    def explain(self, exception: IsADirectoryError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет IsADirectoryError простыми словами
        Explains IsADirectoryError in simple terms
        
        Args:
            exception: IsADirectoryError для объяснения / IsADirectoryError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"📂 Ошибка: это директория, а не файл"
        else:
            explanation = f"📂 Error: this is a directory, not a file"
        
        # Извлекаем путь из сообщения об ошибке
        path = self._extract_path_from_error(error_message)
        if path:
            if self._get_language() == "ru":
                explanation += f"\n📁 Путь: {path}"
            else:
                explanation += f"\n📁 Path: {path}"
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Вы пытаетесь выполнить операцию с файлом над директорией"
        else:
            explanation += "\n💡 You're trying to perform a file operation on a directory"
        
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
    
    def _extract_path_from_error(self, error_message: str) -> Optional[str]:
        """Извлекает путь из сообщения об ошибке / Extracts path from error message"""
        # "Is a directory: 'path'"
        if "'" in error_message:
            parts = error_message.split("'")
            if len(parts) >= 2:
                return parts[1]
        return None
    
    def get_suggestions(self, exception: IsADirectoryError) -> list[str]:
        """Возвращает предложения по исправлению IsADirectoryError / Returns suggestions for fixing IsADirectoryError"""
        if self._get_language() == "ru":
            return [
                "Используйте os.listdir() для чтения содержимого директории",
                "Используйте os.path.isdir() для проверки типа объекта",
                "Укажите конкретный файл внутри директории",
                "Используйте os.walk() для обхода директории",
                "Проверьте, что путь ведет к файлу, а не к директории"
            ]
        else:
            return [
                "Use os.listdir() to read directory contents",
                "Use os.path.isdir() to check object type",
                "Specify a specific file inside the directory",
                "Use os.walk() to traverse the directory",
                "Check that the path leads to a file, not a directory"
            ]
