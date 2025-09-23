"""
Обработчик для ImportError
ImportError handler
"""

import difflib
from typing import Optional, Any
from .base import BaseHandler


class ImportErrorHandler(BaseHandler):
    """Обработчик для ImportError - ошибок импорта модулей
    Handler for ImportError - module import errors"""
    
    def explain(self, exception: ImportError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет ImportError простыми словами
        
        Args:
            exception: ImportError для объяснения
            traceback_obj: Объект трассировки
            
        Returns:
            Человеко-читаемое объяснение
        """
        error_message = str(exception)
        
        # Получаем контекстную информацию
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        if self._get_language() == "ru":
            explanation = f"📦 Ошибка импорта: {error_message}"
        else:
            explanation = f"📦 Import error: {error_message}"
        
        # Анализируем сообщение об ошибке
        if "No module named" in error_message:
            explanation = self._explain_no_module(error_message)
        elif "cannot import name" in error_message:
            explanation = self._explain_cannot_import_name(error_message)
        elif "attempted relative import" in error_message:
            explanation = self._explain_relative_import(error_message)
        elif "bad magic number" in error_message:
            explanation = self._explain_bad_magic_number(error_message)
        
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
    
    def _explain_no_module(self, error_message: str) -> str:
        """Объясняет ошибки отсутствия модуля / Explains missing module errors"""
        # "No module named 'module_name'"
        if "'" in error_message:
            module_name = error_message.split("'")[1]
            if self._get_language() == "ru":
                explanation = f"📦 Модуль '{module_name}' не найден или не установлен"
            else:
                explanation = f"📦 Module '{module_name}' not found or not installed"
            
            # Ищем похожие модули
            similar_modules = self._find_similar_modules(module_name)
            if similar_modules:
                if self._get_language() == "ru":
                    explanation += f"\n🤔 Возможно, вы имели в виду: {similar_modules[0]}"
                    if len(similar_modules) > 1:
                        explanation += f"\n🔧 Установите пакет: pip install {similar_modules[0]}"
                else:
                    explanation += f"\n🤔 Perhaps you meant: {similar_modules[0]}"
                    if len(similar_modules) > 1:
                        explanation += f"\n🔧 Install package: pip install {similar_modules[0]}"
            
            return explanation
        else:
            if self._get_language() == "ru":
                return "📦 Модуль не найден или не установлен"
            else:
                return "📦 Module not found or not installed"
    
    def _explain_cannot_import_name(self, error_message: str) -> str:
        """Объясняет ошибки импорта конкретного имени"""
        # "cannot import name 'function_name' from 'module_name'"
        if "from" in error_message and "'" in error_message:
            parts = error_message.split("'")
            if len(parts) >= 4:
                name = parts[1]
                module = parts[3]
                return f"📦 Не удалось импортировать '{name}' из модуля '{module}'"
        return "📦 Не удалось импортировать указанное имя из модуля"
    
    def _explain_relative_import(self, error_message: str) -> str:
        """Объясняет ошибки относительного импорта"""
        return "📦 Ошибка относительного импорта. Убедитесь, что используете правильный синтаксис: from .module import name"
    
    def _explain_bad_magic_number(self, error_message: str) -> str:
        """Объясняет ошибки неверного магического числа"""
        return "📦 Файл .pyc поврежден или несовместим. Удалите файлы __pycache__ и перезапустите программу"
    
    def _find_similar_modules(self, module_name: str) -> list[str]:
        """
        Находит модули, похожие на искомый
        
        Args:
            module_name: Имя искомого модуля
            
        Returns:
            Список похожих модулей
        """
        # Популярные модули Python
        popular_modules = [
            'numpy', 'pandas', 'matplotlib', 'requests', 'flask', 'django',
            'tensorflow', 'torch', 'scikit-learn', 'opencv-python', 'pillow',
            'beautifulsoup4', 'selenium', 'scrapy', 'fastapi', 'uvicorn',
            'sqlalchemy', 'psycopg2', 'pymongo', 'redis', 'celery',
            'jupyter', 'notebook', 'ipython', 'pytest', 'black', 'flake8',
            'click', 'typer', 'rich', 'tqdm', 'colorama', 'termcolor',
            'pyyaml', 'toml', 'python-dotenv', 'environs', 'pydantic',
            'httpx', 'aiohttp', 'websockets', 'asyncio', 'concurrent',
            'multiprocessing', 'threading', 'queue', 'collections',
            'itertools', 'functools', 'operator', 'pathlib', 'os', 'sys',
            'json', 'csv', 'xml', 'html', 'urllib', 'http', 'socket',
            'ssl', 'hashlib', 'base64', 'uuid', 'datetime', 'time',
            'calendar', 'math', 'statistics', 'random', 'secrets',
            're', 'string', 'textwrap', 'unicodedata', 'codecs',
            'io', 'tempfile', 'shutil', 'glob', 'fnmatch', 'linecache',
            'pickle', 'shelve', 'dbm', 'sqlite3', 'zlib', 'gzip',
            'bz2', 'lzma', 'tarfile', 'zipfile', 'configparser',
            'argparse', 'getopt', 'logging', 'warnings', 'traceback',
            'inspect', 'ast', 'dis', 'types', 'typing', 'dataclasses',
            'enum', 'abc', 'contextlib', 'weakref', 'gc', 'copy',
            'pprint', 'reprlib', 'numbers', 'decimal', 'fractions',
            'cmath', 'array', 'struct', 'memoryview', 'mmap'
        ]
        
        # Используем difflib для поиска похожих модулей
        similar = difflib.get_close_matches(module_name, popular_modules, n=3, cutoff=0.6)
        
        return similar
    
    def get_suggestions(self, exception: ImportError) -> list[str]:
        """Возвращает предложения по исправлению ImportError / Returns suggestions for fixing ImportError"""
        error_message = str(exception)
        
        if "No module named" in error_message:
            if self._get_language() == "ru":
                return [
                    "Установите модуль: pip install module_name",
                    "Проверьте, что модуль установлен: pip list | grep module_name",
                    "Убедитесь, что используете правильное имя модуля",
                    "Проверьте, что модуль находится в PYTHONPATH",
                    "Попробуйте переустановить модуль: pip uninstall module_name && pip install module_name"
                ]
            else:
                return [
                    "Install the module: pip install module_name",
                    "Check if module is installed: pip list | grep module_name",
                    "Make sure you're using the correct module name",
                    "Check that the module is in PYTHONPATH",
                    "Try reinstalling the module: pip uninstall module_name && pip install module_name"
                ]
        elif "cannot import name" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте, что имя существует в модуле: dir(module_name)",
                    "Убедитесь, что используете правильное имя",
                    "Проверьте версию модуля - имя могло измениться",
                    "Импортируйте весь модуль: import module_name",
                    "Проверьте документацию модуля"
                ]
            else:
                return [
                    "Check if the name exists in the module: dir(module_name)",
                    "Make sure you're using the correct name",
                    "Check the module version - the name might have changed",
                    "Import the entire module: import module_name",
                    "Check the module documentation"
                ]
        elif "attempted relative import" in error_message:
            return [
                "Используйте абсолютный импорт вместо относительного",
                "Убедитесь, что файл запускается как модуль: python -m package.module",
                "Проверьте структуру пакета и __init__.py файлы",
                "Используйте sys.path для добавления пути к модулю"
            ]
        else:
            return [
                "Проверьте правильность синтаксиса импорта",
                "Убедитесь, что модуль существует и доступен",
                "Проверьте права доступа к файлам модуля",
                "Попробуйте перезапустить интерпретатор Python"
            ]
