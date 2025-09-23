#!/usr/bin/env python3
"""
Тесты для основного модуля friendly_exceptions
Tests for friendly_exceptions core module
"""

import pytest
import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from friendly_exceptions.core import (
    set_language,
    get_language,
    explain_exception,
    FriendlyException
)


class TestLanguageSwitching:
    """Тесты переключения языков"""
    
    def test_set_language_valid(self):
        """Тест установки валидного языка"""
        # Тестируем русский
        set_language("ru")
        assert get_language() == "ru"
        
        # Тестируем английский
        set_language("en")
        assert get_language() == "en"
        
        # Тестируем регистр
        set_language("RU")
        assert get_language() == "ru"
        
        set_language("EN")
        assert get_language() == "en"
    
    def test_set_language_invalid(self):
        """Тест установки невалидного языка"""
        original_language = get_language()
        
        # Пытаемся установить невалидный язык
        set_language("invalid")
        
        # Язык должен остаться прежним
        assert get_language() == original_language
    
    def test_get_language(self):
        """Тест получения текущего языка"""
        language = get_language()
        assert language in ["ru", "en"]


class TestExplainException:
    """Тесты функции explain_exception"""
    
    def test_explain_attribute_error(self):
        """Тест объяснения AttributeError"""
        exception = AttributeError("'Test' object has no attribute 'nmae'")
        result = explain_exception(exception)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "🔍" in result
    
    def test_explain_key_error(self):
        """Тест объяснения KeyError"""
        exception = KeyError("user_id")
        result = explain_exception(exception)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "🔑" in result
    
    def test_explain_unknown_error(self):
        """Тест объяснения неизвестной ошибки"""
        class CustomError(Exception):
            pass
        
        exception = CustomError("Custom error message")
        result = explain_exception(exception)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "❓" in result


class TestFriendlyException:
    """Тесты класса FriendlyException"""
    
    def test_friendly_exception_creation(self):
        """Тест создания FriendlyException"""
        original = AttributeError("test")
        friendly = FriendlyException(original, "Friendly message")
        
        assert friendly.original_exception == original
        assert friendly.friendly_message == "Friendly message"
        assert str(friendly) == "Friendly message"
    
    def test_friendly_exception_inheritance(self):
        """Тест наследования FriendlyException"""
        original = ValueError("test")
        friendly = FriendlyException(original, "Friendly message")
        
        assert isinstance(friendly, Exception)
        assert isinstance(friendly, FriendlyException)


if __name__ == "__main__":
    pytest.main([__file__])
