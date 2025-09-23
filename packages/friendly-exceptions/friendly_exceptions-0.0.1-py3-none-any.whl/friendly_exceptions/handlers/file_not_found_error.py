"""
Обработчик для FileNotFoundError
FileNotFoundError handler
"""

import os
from typing import Optional, Any
from .base import BaseHandler


class FileNotFoundErrorHandler(BaseHandler):
    """Обработчик для FileNotFoundError - ошибок отсутствия файлов
    Handler for FileNotFoundError - file not found errors"""
    
    def explain(self, exception: FileNotFoundError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет FileNotFoundError простыми словами
        Explains FileNotFoundError in simple terms
        
        Args:
            exception: FileNotFoundError для объяснения / FileNotFoundError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        # Получаем контекстную информацию
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Извлекаем имя файла из сообщения об ошибке
        filename = self._extract_filename(error_message)
        
        if self._get_language() == "ru":
            explanation = f"📁 Файл не найден: {filename}"
        else:
            explanation = f"📁 File not found: {filename}"
        
        # Проверяем, существует ли файл в текущей директории
        if filename:
            current_dir_files = self._get_current_directory_files()
            similar_files = self._find_similar_files(filename, current_dir_files)
            
            if similar_files:
                if self._get_language() == "ru":
                    explanation += f"\n🤔 Возможно, вы имели в виду: {', '.join(similar_files[:3])}"
                else:
                    explanation += f"\n🤔 Perhaps you meant: {', '.join(similar_files[:3])}"
            
            # Проверяем, есть ли файл в других местах
            if not os.path.exists(filename):
                suggestions = self._get_file_suggestions(filename)
                if suggestions:
                    if self._get_language() == "ru":
                        explanation += f"\n💡 Возможные решения:"
                    else:
                        explanation += f"\n💡 Possible solutions:"
                    for suggestion in suggestions:
                        explanation += f"\n  • {suggestion}"
        
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
    
    def _extract_filename(self, error_message: str) -> str:
        """Извлекает имя файла из сообщения об ошибке / Extracts filename from error message"""
        # "No such file or directory: 'filename'"
        if "'" in error_message:
            parts = error_message.split("'")
            if len(parts) >= 2:
                return parts[1]
        return "unknown"
    
    def _get_current_directory_files(self) -> list[str]:
        """Получает список файлов в текущей директории / Gets list of files in current directory"""
        try:
            return os.listdir(".")
        except Exception:
            return []
    
    def _find_similar_files(self, target_filename: str, files: list[str]) -> list[str]:
        """Находит похожие файлы / Finds similar files"""
        import difflib
        
        # Фильтруем только файлы (не директории)
        file_list = [f for f in files if os.path.isfile(f)]
        
        # Ищем похожие имена файлов
        similar = difflib.get_close_matches(target_filename, file_list, n=3, cutoff=0.6)
        
        return similar
    
    def _get_file_suggestions(self, filename: str) -> list[str]:
        """Получает предложения по файлу / Gets file suggestions"""
        suggestions = []
        
        if self._get_language() == "ru":
            if not filename.startswith("/") and not ":" in filename:
                suggestions.append("Проверьте, что файл находится в правильной директории")
                suggestions.append("Используйте абсолютный путь к файлу")
            
            if filename.endswith(".py"):
                suggestions.append("Убедитесь, что модуль установлен: pip install module_name")
            
            suggestions.append("Проверьте права доступа к файлу")
            suggestions.append("Убедитесь, что файл не был перемещен или удален")
        else:
            if not filename.startswith("/") and not ":" in filename:
                suggestions.append("Check that the file is in the correct directory")
                suggestions.append("Use absolute path to the file")
            
            if filename.endswith(".py"):
                suggestions.append("Make sure the module is installed: pip install module_name")
            
            suggestions.append("Check file permissions")
            suggestions.append("Make sure the file wasn't moved or deleted")
        
        return suggestions
    
    def get_suggestions(self, exception: FileNotFoundError) -> list[str]:
        """Возвращает предложения по исправлению FileNotFoundError / Returns suggestions for fixing FileNotFoundError"""
        if self._get_language() == "ru":
            return [
                "Проверьте правильность пути к файлу",
                "Убедитесь, что файл существует: os.path.exists('filename')",
                "Проверьте права доступа к файлу и директории",
                "Используйте абсолютный путь вместо относительного",
                "Создайте файл, если он должен существовать",
                "Проверьте, что файл не был перемещен или переименован"
            ]
        else:
            return [
                "Check the file path is correct",
                "Make sure the file exists: os.path.exists('filename')",
                "Check file and directory permissions",
                "Use absolute path instead of relative",
                "Create the file if it should exist",
                "Check that the file wasn't moved or renamed"
            ]