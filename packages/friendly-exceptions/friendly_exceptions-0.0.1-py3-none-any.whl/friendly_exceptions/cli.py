#!/usr/bin/env python3
"""
Command Line Interface for friendly_exceptions
"""

import sys
import argparse
from typing import Optional
from .core import set_language, get_language, explain_exception


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Friendly Exceptions - Human-readable error explanations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  friendly-exceptions --language en
  friendly-exceptions --test
  friendly-exceptions --version
        """
    )
    
    parser.add_argument(
        "--language", "-l",
        choices=["ru", "en"],
        help="Set language for error messages (ru/en)"
    )
    
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Run a test to demonstrate the library"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="friendly-exceptions 1.0.0"
    )
    
    parser.add_argument(
        "--current-language",
        action="store_true",
        help="Show current language setting"
    )
    
    args = parser.parse_args()
    
    # Устанавливаем язык, если указан
    if args.language:
        set_language(args.language)
        print(f"Language set to: {args.language}")
        return 0
    
    # Показываем текущий язык
    if args.current_language:
        print(f"Current language: {get_language()}")
        return 0
    
    # Запускаем тест
    if args.test:
        run_test()
        return 0
    
    # Если аргументы не указаны, показываем справку
    parser.print_help()
    return 0


def run_test():
    """Запускает демонстрационный тест / Runs demonstration test"""
    print("🧪 Running friendly_exceptions test...")
    print("=" * 50)
    
    # Тест AttributeError
    print("\n1. Testing AttributeError:")
    try:
        class Test:
            def __init__(self):
                self.name = "test"
        
        t = Test()
        print(t.nmae)  # Опечатка в атрибуте
    except Exception as e:
        print(f"Exception caught: {e}")
        explain_exception(e)
    
    # Тест KeyError
    print("\n2. Testing KeyError:")
    try:
        data = {"user": "john", "age": 25}
        print(data["user_id"])  # Несуществующий ключ
    except Exception as e:
        print(f"Exception caught: {e}")
        explain_exception(e)
    
    # Тест ImportError
    print("\n3. Testing ImportError:")
    try:
        import nonexistent_module  # Несуществующий модуль
    except Exception as e:
        print(f"Exception caught: {e}")
        explain_exception(e)
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    sys.exit(main())
