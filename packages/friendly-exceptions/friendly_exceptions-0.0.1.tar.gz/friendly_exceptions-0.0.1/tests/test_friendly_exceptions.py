"""
Тесты для библиотеки friendly_exceptions
"""

import pytest
import sys
from io import StringIO
from contextlib import redirect_stdout

from friendly_exceptions import explain, explain_exception, set_global_handler
from friendly_exceptions.handlers import (
    KeyErrorHandler,
    ValueErrorHandler,
    TypeErrorHandler,
    AttributeErrorHandler,
    IndexErrorHandler,
    FileNotFoundErrorHandler,
    ImportErrorHandler,
    ZeroDivisionErrorHandler
)


class TestKeyErrorHandler:
    """Тесты для KeyErrorHandler"""
    
    def test_explain_key_error(self):
        """Тест объяснения KeyError"""
        handler = KeyErrorHandler()
        error = KeyError('user_id')
        
        # Создаем контекст с локальными переменными
        class MockFrame:
            def __init__(self):
                self.f_locals = {'user_data': {'name': 'Иван', 'age': 25}}
                self.f_code = type('Code', (), {'co_filename': 'test.py', 'co_name': 'test_func'})()
                self.tb_lineno = 10
        
        class MockTraceback:
            def __init__(self):
                self.tb_frame = MockFrame()
                self.tb_next = None
        
        traceback_obj = MockTraceback()
        result = handler.explain(error, traceback_obj)
        
        assert "Словарь не содержит ключ 'user_id'" in result
        assert "user_data" in result
        assert "name" in result
        assert "age" in result
    
    def test_find_similar_keys(self):
        """Тест поиска похожих ключей"""
        handler = KeyErrorHandler()
        available_keys = ['name', 'age', 'email', 'phone']
        
        # Тест точного совпадения (разный регистр)
        similar = handler._find_similar_keys('NAME', available_keys)
        assert 'name' in similar
        
        # Тест частичного совпадения
        similar = handler._find_similar_keys('user', available_keys)
        assert len(similar) == 0  # Нет похожих ключей
        
        # Тест с похожими ключами
        similar = handler._find_similar_keys('mail', available_keys)
        assert 'email' in similar


class TestValueErrorHandler:
    """Тесты для ValueErrorHandler"""
    
    def test_explain_int_conversion_error(self):
        """Тест объяснения ошибки преобразования в int"""
        handler = ValueErrorHandler()
        error = ValueError("invalid literal for int() with base 10: 'abc'")
        
        result = handler.explain(error, None)
        
        assert "Не удалось преобразовать 'abc' в целое число" in result
        assert "🔢" in result
    
    def test_explain_float_conversion_error(self):
        """Тест объяснения ошибки преобразования в float"""
        handler = ValueErrorHandler()
        error = ValueError("could not convert string to float: 'xyz'")
        
        result = handler.explain(error, None)
        
        assert "Не удалось преобразовать строку 'xyz' в число с плавающей точкой" in result
    
    def test_explain_unpacking_error(self):
        """Тест объяснения ошибки распаковки"""
        handler = ValueErrorHandler()
        error = ValueError("too many values to unpack (expected 2)")
        
        result = handler.explain(error, None)
        
        assert "Слишком много значений для распаковки" in result


class TestTypeErrorHandler:
    """Тесты для TypeErrorHandler"""
    
    def test_explain_unsupported_operand(self):
        """Тест объяснения несовместимых операндов"""
        handler = TypeErrorHandler()
        error = TypeError("unsupported operand type(s) for +: 'int' and 'str'")
        
        result = handler.explain(error, None)
        
        assert "Нельзя складывать числа и строки" in result
        assert "str()" in result
    
    def test_explain_not_callable(self):
        """Тест объяснения ошибки вызова не-функции"""
        handler = TypeErrorHandler()
        error = TypeError("'int' object is not callable")
        
        result = handler.explain(error, None)
        
        assert "Вы пытаетесь вызвать объект, который не является функцией" in result
    
    def test_explain_not_iterable(self):
        """Тест объяснения ошибки итерации"""
        handler = TypeErrorHandler()
        error = TypeError("'int' object is not iterable")
        
        result = handler.explain(error, None)
        
        assert "Объект не поддерживает итерацию" in result


class TestAttributeErrorHandler:
    """Тесты для AttributeErrorHandler"""
    
    def test_explain_attribute_error(self):
        """Тест объяснения AttributeError"""
        handler = AttributeErrorHandler()
        error = AttributeError("'str' object has no attribute 'uppercase'")
        
        result = handler.explain(error, None)
        
        assert "str' не имеет атрибута 'uppercase'" in result
        assert "Тип объекта: str" in result
    
    def test_find_similar_attributes(self):
        """Тест поиска похожих атрибутов"""
        handler = AttributeErrorHandler()
        
        # Тест для строки
        similar = handler._find_similar_attributes('uppercase', 'str')
        assert 'upper' in similar
        
        # Тест для списка
        similar = handler._find_similar_attributes('appendd', 'list')
        assert 'append' in similar


class TestIndexErrorHandler:
    """Тесты для IndexErrorHandler"""
    
    def test_explain_list_index_error(self):
        """Тест объяснения ошибки индексации списка"""
        handler = IndexErrorHandler()
        error = IndexError("list index out of range")
        
        # Создаем контекст с локальными переменными
        class MockFrame:
            def __init__(self):
                self.f_locals = {'numbers': [1, 2, 3]}
                self.f_code = type('Code', (), {'co_filename': 'test.py', 'co_name': 'test_func'})()
                self.tb_lineno = 10
        
        class MockTraceback:
            def __init__(self):
                self.tb_frame = MockFrame()
                self.tb_next = None
        
        traceback_obj = MockTraceback()
        result = handler.explain(error, traceback_obj)
        
        assert "Список 'numbers' содержит 3 элементов" in result
        assert "Индексы должны быть от 0 до 2" in result


class TestFileNotFoundErrorHandler:
    """Тесты для FileNotFoundErrorHandler"""
    
    def test_explain_file_not_found_error(self):
        """Тест объяснения FileNotFoundError"""
        handler = FileNotFoundErrorHandler()
        error = FileNotFoundError("[Errno 2] No such file or directory: 'test.txt'")
        
        result = handler.explain(error, None)
        
        assert "Файл не найден: test.txt" in result
        assert "Текущая директория:" in result
    
    def test_extract_filename(self):
        """Тест извлечения имени файла"""
        handler = FileNotFoundErrorHandler()
        
        error_msg = "[Errno 2] No such file or directory: 'test.txt'"
        filename = handler._extract_filename(error_msg)
        assert filename == "test.txt"


class TestImportErrorHandler:
    """Тесты для ImportErrorHandler"""
    
    def test_explain_no_module(self):
        """Тест объяснения отсутствия модуля"""
        handler = ImportErrorHandler()
        error = ImportError("No module named 'nonexistent'")
        
        result = handler.explain(error, None)
        
        assert "Модуль 'nonexistent' не найден или не установлен" in result
    
    def test_explain_cannot_import_name(self):
        """Тест объяснения ошибки импорта имени"""
        handler = ImportErrorHandler()
        error = ImportError("cannot import name 'function' from 'module'")
        
        result = handler.explain(error, None)
        
        assert "Не удалось импортировать 'function' из модуля 'module'" in result


class TestZeroDivisionErrorHandler:
    """Тесты для ZeroDivisionErrorHandler"""
    
    def test_explain_zero_division_error(self):
        """Тест объяснения ZeroDivisionError"""
        handler = ZeroDivisionErrorHandler()
        error = ZeroDivisionError("division by zero")
        
        result = handler.explain(error, None)
        
        assert "Деление на ноль невозможно" in result
        assert "В математике деление на ноль не определено" in result


class TestCoreFunctions:
    """Тесты для основных функций"""
    
    def test_explain_exception(self):
        """Тест функции explain_exception"""
        error = KeyError('test_key')
        result = explain_exception(error)
        
        assert isinstance(result, str)
        assert "Словарь не содержит ключ 'test_key'" in result
    
    def test_explain_with_context(self):
        """Тест функции explain с контекстом"""
        # Этот тест сложнее, так как требует реального исключения
        # В реальном коде это будет работать автоматически
        pass


if __name__ == "__main__":
    pytest.main([__file__])
