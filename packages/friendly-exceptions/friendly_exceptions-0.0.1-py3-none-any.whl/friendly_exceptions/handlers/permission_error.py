"""
Обработчик для PermissionError
PermissionError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class PermissionErrorHandler(BaseHandler):
    """Обработчик для PermissionError - ошибок прав доступа
    Handler for PermissionError - permission errors"""
    
    def explain(self, exception: PermissionError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет PermissionError простыми словами
        Explains PermissionError in simple terms
        
        Args:
            exception: PermissionError для объяснения / PermissionError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"🔒 Ошибка прав доступа: {error_message}"
        else:
            explanation = f"🔒 Permission error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем файл в локальных переменных
        file_path = self._find_file_in_context(locals_dict)
        if file_path:
            if self._get_language() == "ru":
                explanation += f"\n📁 Файл: {file_path}"
            else:
                explanation += f"\n📁 File: {file_path}"
        
        # Добавляем информацию о правах
        if self._get_language() == "ru":
            explanation += "\n💡 У вас недостаточно прав для выполнения этой операции"
        else:
            explanation += "\n💡 You don't have sufficient permissions to perform this operation"
        
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
    
    def _find_file_in_context(self, locals_dict: dict) -> Optional[str]:
        """Ищет файл в контексте / Finds file in context"""
        # Ищем переменные, которые могут содержать путь к файлу
        file_indicators = ['file', 'path', 'filename', 'filepath', 'f']
        
        for var_name, var_value in locals_dict.items():
            if var_name.lower() in file_indicators:
                if isinstance(var_value, str) and ('/' in var_value or '\\' in var_value):
                    return var_value
        
        return None
    
    def get_suggestions(self, exception: PermissionError) -> list[str]:
        """Возвращает предложения по исправлению PermissionError / Returns suggestions for fixing PermissionError"""
        if self._get_language() == "ru":
            return [
                "Запустите программу с правами администратора",
                "Проверьте права доступа к файлу: ls -l filename",
                "Измените права доступа: chmod +x filename",
                "Проверьте, что файл не заблокирован другим процессом",
                "Убедитесь, что у вас есть права на запись в директорию",
                "Проверьте, что файл не только для чтения"
            ]
        else:
            return [
                "Run the program as administrator",
                "Check file permissions: ls -l filename",
                "Change file permissions: chmod +x filename",
                "Check that the file is not locked by another process",
                "Make sure you have write permissions to the directory",
                "Check that the file is not read-only"
            ]
