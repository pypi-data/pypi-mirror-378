"""
Обработчик для OSError и связанных ошибок
OSError and related errors handler
"""

import os
from typing import Optional, Any
from .base import BaseHandler


class OSErrorHandler(BaseHandler):
    """Обработчик для OSError - ошибок операционной системы
    Handler for OSError - operating system errors"""
    
    def explain(self, exception: OSError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет OSError простыми словами
        Explains OSError in simple terms
        
        Args:
            exception: OSError для объяснения / OSError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        errno = getattr(exception, 'errno', None)
        
        if self._get_language() == "ru":
            explanation = f"💻 Ошибка операционной системы: {error_message}"
        else:
            explanation = f"💻 Operating system error: {error_message}"
        
        # Анализируем конкретные типы ошибок
        if errno:
            explanation += self._explain_by_errno(errno)
        
        # Анализируем сообщение об ошибке
        if "Permission denied" in error_message or "permission denied" in error_message:
            explanation = self._explain_permission_denied(error_message)
        elif "No such file or directory" in error_message:
            explanation = self._explain_file_not_found(error_message)
        elif "Is a directory" in error_message:
            explanation = self._explain_is_directory(error_message)
        elif "Not a directory" in error_message:
            explanation = self._explain_not_directory(error_message)
        elif "Device or resource busy" in error_message:
            explanation = self._explain_device_busy(error_message)
        elif "No space left" in error_message:
            explanation = self._explain_no_space(error_message)
        
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
    
    def _explain_by_errno(self, errno: int) -> str:
        """Объясняет ошибку по коду errno / Explains error by errno code"""
        errno_explanations = {
            1: "Operation not permitted",
            2: "No such file or directory", 
            3: "No such process",
            4: "Interrupted system call",
            5: "Input/output error",
            6: "No such device or address",
            7: "Argument list too long",
            8: "Exec format error",
            9: "Bad file descriptor",
            10: "No child processes",
            11: "Resource temporarily unavailable",
            12: "Cannot allocate memory",
            13: "Permission denied",
            14: "Bad address",
            15: "Block device required",
            16: "Device or resource busy",
            17: "File exists",
            18: "Invalid cross-device link",
            19: "No such device",
            20: "Not a directory",
            21: "Is a directory",
            22: "Invalid argument",
            23: "Too many open files in system",
            24: "Too many open files",
            25: "Inappropriate ioctl for device",
            26: "Text file busy",
            27: "File too large",
            28: "No space left on device",
            29: "Illegal seek",
            30: "Read-only file system",
            31: "Too many links",
            32: "Broken pipe",
            33: "Numerical argument out of domain",
            34: "Numerical result out of range",
            35: "Resource deadlock avoided",
            36: "File name too long",
            37: "No locks available",
            38: "Function not implemented",
            39: "Directory not empty",
            40: "Too many levels of symbolic links",
        }
        
        explanation = errno_explanations.get(errno, "")
        if explanation:
            if self._get_language() == "ru":
                return f"\n📋 Код ошибки {errno}: {explanation}"
            else:
                return f"\n📋 Error code {errno}: {explanation}"
        return ""
    
    def _explain_permission_denied(self, error_message: str) -> str:
        """Объясняет ошибку доступа / Explains permission denied error"""
        if self._get_language() == "ru":
            return "🔒 Недостаточно прав доступа для выполнения операции"
        else:
            return "🔒 Insufficient permissions to perform the operation"
    
    def _explain_file_not_found(self, error_message: str) -> str:
        """Объясняет ошибку отсутствия файла / Explains file not found error"""
        if self._get_language() == "ru":
            return "📁 Файл или директория не найдены"
        else:
            return "📁 File or directory not found"
    
    def _explain_is_directory(self, error_message: str) -> str:
        """Объясняет ошибку 'это директория' / Explains 'is a directory' error"""
        if self._get_language() == "ru":
            return "📂 Попытка выполнить операцию с файлом над директорией"
        else:
            return "📂 Attempt to perform file operation on a directory"
    
    def _explain_not_directory(self, error_message: str) -> str:
        """Объясняет ошибку 'не директория' / Explains 'not a directory' error"""
        if self._get_language() == "ru":
            return "📄 Попытка выполнить операцию с директорией над файлом"
        else:
            return "📄 Attempt to perform directory operation on a file"
    
    def _explain_device_busy(self, error_message: str) -> str:
        """Объясняет ошибку 'устройство занято' / Explains 'device busy' error"""
        if self._get_language() == "ru":
            return "⏳ Устройство или ресурс занят другим процессом"
        else:
            return "⏳ Device or resource is busy with another process"
    
    def _explain_no_space(self, error_message: str) -> str:
        """Объясняет ошибку 'нет места' / Explains 'no space' error"""
        if self._get_language() == "ru":
            return "💾 Недостаточно места на диске"
        else:
            return "💾 Not enough disk space"
    
    def get_suggestions(self, exception: OSError) -> list[str]:
        """Возвращает предложения по исправлению OSError / Returns suggestions for fixing OSError"""
        error_message = str(exception)
        
        if "Permission denied" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте права доступа к файлу или директории",
                    "Запустите программу с правами администратора",
                    "Используйте chmod для изменения прав доступа",
                    "Проверьте, что файл не заблокирован другим процессом"
                ]
            else:
                return [
                    "Check file or directory permissions",
                    "Run the program as administrator",
                    "Use chmod to change access permissions",
                    "Check that the file is not locked by another process"
                ]
        elif "No such file or directory" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте правильность пути к файлу",
                    "Убедитесь, что файл существует",
                    "Проверьте, что директория существует",
                    "Используйте абсолютный путь вместо относительного"
                ]
            else:
                return [
                    "Check the file path is correct",
                    "Make sure the file exists",
                    "Check that the directory exists",
                    "Use absolute path instead of relative"
                ]
        elif "No space left" in error_message:
            if self._get_language() == "ru":
                return [
                    "Освободите место на диске",
                    "Удалите ненужные файлы",
                    "Проверьте доступное место: df -h",
                    "Очистите временные файлы"
                ]
            else:
                return [
                    "Free up disk space",
                    "Delete unnecessary files",
                    "Check available space: df -h",
                    "Clean temporary files"
                ]
        else:
            if self._get_language() == "ru":
                return [
                    "Проверьте правильность операции",
                    "Убедитесь, что ресурс доступен",
                    "Проверьте права доступа",
                    "Попробуйте повторить операцию позже"
                ]
            else:
                return [
                    "Check the operation is correct",
                    "Make sure the resource is available",
                    "Check access permissions",
                    "Try the operation again later"
                ]
