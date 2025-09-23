#!/usr/bin/env python3
"""
Примеры работы с конфигурацией friendly_exceptions
Configuration examples for friendly_exceptions
"""

import friendly_exceptions
from friendly_exceptions.config import get_config, set_config, save_config, reset_config

def main():
    print("⚙️ Примеры работы с конфигурацией")
    print("=" * 50)
    
    # Показываем текущую конфигурацию
    print("\n1. Текущая конфигурация:")
    print("-" * 30)
    config = get_config()
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
    
    # Изменяем настройки
    print("\n2. Изменение настроек:")
    print("-" * 30)
    
    # Отключаем показ оригинального traceback
    set_config("show_original_traceback", False)
    print("  Отключен показ оригинального traceback")
    
    # Устанавливаем максимальное количество предложений
    set_config("max_suggestions", 3)
    print("  Установлено максимальное количество предложений: 3")
    
    # Включаем логирование в файл
    set_config("log_file", "friendly_exceptions.log")
    print("  Включено логирование в файл: friendly_exceptions.log")
    
    # Сохраняем конфигурацию
    save_config()
    print("  Конфигурация сохранена")
    
    # Тестируем с новыми настройками
    print("\n3. Тест с новыми настройками:")
    print("-" * 30)
    
    try:
        data = {"user": "admin"}
        print(data["password"])  # KeyError
    except:
        pass  # Ошибка будет обработана с новыми настройками
    
    # Сбрасываем конфигурацию
    print("\n4. Сброс конфигурации:")
    print("-" * 30)
    reset_config()
    print("  Конфигурация сброшена к значениям по умолчанию")
    
    # Показываем сброшенную конфигурацию
    print("\n5. Конфигурация после сброса:")
    print("-" * 30)
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    print("✅ Демонстрация конфигурации завершена!")

if __name__ == "__main__":
    main()
