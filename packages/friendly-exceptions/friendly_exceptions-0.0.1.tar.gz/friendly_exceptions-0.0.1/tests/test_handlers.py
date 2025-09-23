#!/usr/bin/env python3
"""
Тесты для обработчиков исключений
Tests for exception handlers
"""

import pytest
import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from friendly_exceptions.handlers import (
    AttributeErrorHandler,
    KeyErrorHandler,
    ImportErrorHandler,
    TypeErrorHandler,
    IndexErrorHandler,
    ValueErrorHandler,
    FileNotFoundErrorHandler,
    ZeroDivisionErrorHandler
)


class TestAttributeErrorHandler:
    """Тесты для AttributeErrorHandler"""
    
    def test_explain_basic(self):
        """Тест базового объяснения AttributeError"""
        handler = AttributeErrorHandler()
        exception = AttributeError("'Test' object has no attribute 'nmae'")
        
        result = handler.explain(exception, None)
        
        assert "🔍" in result
        assert "nmae" in result
        assert "Test" in result
    
    def test_explain_with_suggestions(self):
        """Тест объяснения с предложениями"""
        handler = AttributeErrorHandler()
        exception = AttributeError("'Test' object has no attribute 'nmae'")
        
        result = handler.explain(exception, None)
        
        assert "💡" in result or "🔧" in result
    
    def test_get_suggestions(self):
        """Тест получения предложений"""
        handler = AttributeErrorHandler()
        exception = AttributeError("'Test' object has no attribute 'nmae'")
        
        suggestions = handler.get_suggestions(exception)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestKeyErrorHandler:
    """Тесты для KeyErrorHandler"""
    
    def test_explain_basic(self):
        """Тест базового объяснения KeyError"""
        handler = KeyErrorHandler()
        exception = KeyError("user_id")
        
        result = handler.explain(exception, None)
        
        assert "🔑" in result
        assert "user_id" in result
    
    def test_get_suggestions(self):
        """Тест получения предложений"""
        handler = KeyErrorHandler()
        exception = KeyError("user_id")
        
        suggestions = handler.get_suggestions(exception)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestImportErrorHandler:
    """Тесты для ImportErrorHandler"""
    
    def test_explain_no_module(self):
        """Тест объяснения отсутствующего модуля"""
        handler = ImportErrorHandler()
        exception = ImportError("No module named 'nonexistent'")
        
        result = handler.explain(exception, None)
        
        assert "📦" in result
        assert "nonexistent" in result
    
    def test_get_suggestions(self):
        """Тест получения предложений"""
        handler = ImportErrorHandler()
        exception = ImportError("No module named 'nonexistent'")
        
        suggestions = handler.get_suggestions(exception)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestTypeErrorHandler:
    """Тесты для TypeErrorHandler"""
    
    def test_explain_basic(self):
        """Тест базового объяснения TypeError"""
        handler = TypeErrorHandler()
        exception = TypeError("can only concatenate str (not 'int') to str")
        
        result = handler.explain(exception, None)
        
        assert "🔧" in result
    
    def test_get_suggestions(self):
        """Тест получения предложений"""
        handler = TypeErrorHandler()
        exception = TypeError("can only concatenate str (not 'int') to str")
        
        suggestions = handler.get_suggestions(exception)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestIndexErrorHandler:
    """Тесты для IndexErrorHandler"""
    
    def test_explain_basic(self):
        """Тест базового объяснения IndexError"""
        handler = IndexErrorHandler()
        exception = IndexError("list index out of range")
        
        result = handler.explain(exception, None)
        
        assert "📊" in result
    
    def test_get_suggestions(self):
        """Тест получения предложений"""
        handler = IndexErrorHandler()
        exception = IndexError("list index out of range")
        
        suggestions = handler.get_suggestions(exception)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestValueErrorHandler:
    """Тесты для ValueErrorHandler"""
    
    def test_explain_basic(self):
        """Тест базового объяснения ValueError"""
        handler = ValueErrorHandler()
        exception = ValueError("invalid literal for int() with base 10: 'abc'")
        
        result = handler.explain(exception, None)
        
        assert "⚠️" in result
    
    def test_get_suggestions(self):
        """Тест получения предложений"""
        handler = ValueErrorHandler()
        exception = ValueError("invalid literal for int() with base 10: 'abc'")
        
        suggestions = handler.get_suggestions(exception)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestFileNotFoundErrorHandler:
    """Тесты для FileNotFoundErrorHandler"""
    
    def test_explain_basic(self):
        """Тест базового объяснения FileNotFoundError"""
        handler = FileNotFoundErrorHandler()
        exception = FileNotFoundError("No such file or directory: 'test.txt'")
        
        result = handler.explain(exception, None)
        
        assert "📁" in result
        assert "test.txt" in result
    
    def test_get_suggestions(self):
        """Тест получения предложений"""
        handler = FileNotFoundErrorHandler()
        exception = FileNotFoundError("No such file or directory: 'test.txt'")
        
        suggestions = handler.get_suggestions(exception)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


class TestZeroDivisionErrorHandler:
    """Тесты для ZeroDivisionErrorHandler"""
    
    def test_explain_basic(self):
        """Тест базового объяснения ZeroDivisionError"""
        handler = ZeroDivisionErrorHandler()
        exception = ZeroDivisionError("division by zero")
        
        result = handler.explain(exception, None)
        
        assert "🚫" in result
    
    def test_get_suggestions(self):
        """Тест получения предложений"""
        handler = ZeroDivisionErrorHandler()
        exception = ZeroDivisionError("division by zero")
        
        suggestions = handler.get_suggestions(exception)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0


if __name__ == "__main__":
    pytest.main([__file__])
