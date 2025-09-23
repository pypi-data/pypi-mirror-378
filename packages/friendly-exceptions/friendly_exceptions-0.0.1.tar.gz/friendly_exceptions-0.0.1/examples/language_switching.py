#!/usr/bin/env python3
"""
Примеры переключения языков в friendly_exceptions
Language switching examples for friendly_exceptions
"""

import friendly_exceptions

def test_russian():
    """Тест на русском языке"""
    print("🇷🇺 Тестирование на русском языке")
    print("-" * 40)
    
    try:
        class Test:
            def __init__(self):
                self.name = "тест"
        
        t = Test()
        print(t.nmae)  # Опечатка
    except:
        pass

def test_english():
    """Тест на английском языке"""
    print("🇺🇸 Testing in English")
    print("-" * 40)
    
    try:
        class Test:
            def __init__(self):
                self.name = "test"
        
        t = Test()
        print(t.nmae)  # Typo
    except:
        pass

def main():
    print("🌍 Примеры переключения языков")
    print("=" * 50)
    
    # Русский язык (по умолчанию)
    test_russian()
    
    # Переключение на английский
    print("\n🔄 Переключение на английский...")
    friendly_exceptions.set_language("en")
    
    test_english()
    
    # Переключение обратно на русский
    print("\n🔄 Переключение обратно на русский...")
    friendly_exceptions.set_language("ru")
    
    test_russian()
    
    print("\n" + "=" * 50)
    print("✅ Демонстрация завершена!")
    print(f"Текущий язык: {friendly_exceptions.get_language()}")

if __name__ == "__main__":
    main()
