#!/usr/bin/env python3
"""
Базовые примеры использования friendly_exceptions
Basic usage examples for friendly_exceptions
"""

import friendly_exceptions

def main():
    print("🔍 Базовые примеры использования friendly_exceptions")
    print("=" * 60)
    
    # Пример 1: AttributeError
    print("\n1. AttributeError - ошибка доступа к несуществующему атрибуту")
    print("-" * 50)
    try:
        class Person:
            def __init__(self, name, age):
                self.name = name
                self.age = age
        
        person = Person("Иван", 25)
        print(person.nmae)  # Опечатка в атрибуте
    except:
        pass  # Ошибка будет обработана автоматически
    
    # Пример 2: KeyError
    print("\n2. KeyError - ошибка доступа к несуществующему ключу")
    print("-" * 50)
    try:
        data = {
            "name": "Анна",
            "age": 30,
            "city": "Москва"
        }
        print(data["email"])  # Несуществующий ключ
    except:
        pass
    
    # Пример 3: TypeError
    print("\n3. TypeError - ошибка несовместимости типов")
    print("-" * 50)
    try:
        result = "Привет" + 42  # Сложение строки и числа
    except:
        pass
    
    # Пример 4: IndexError
    print("\n4. IndexError - ошибка выхода за границы индекса")
    print("-" * 50)
    try:
        numbers = [1, 2, 3, 4, 5]
        print(numbers[10])  # Индекс вне диапазона
    except:
        pass
    
    # Пример 5: ValueError
    print("\n5. ValueError - ошибка значения")
    print("-" * 50)
    try:
        number = int("не число")  # Неверное преобразование
    except:
        pass
    
    # Пример 6: ZeroDivisionError
    print("\n6. ZeroDivisionError - деление на ноль")
    print("-" * 50)
    try:
        result = 10 / 0  # Деление на ноль
    except:
        pass
    
    print("\n" + "=" * 60)
    print("✅ Все примеры выполнены!")

if __name__ == "__main__":
    main()
