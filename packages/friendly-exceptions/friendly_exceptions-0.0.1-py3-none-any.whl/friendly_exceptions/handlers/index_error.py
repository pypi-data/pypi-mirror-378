"""
Обработчик для IndexError
IndexError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class IndexErrorHandler(BaseHandler):
    """Обработчик для IndexError - ошибок выхода за границы индекса
    Handler for IndexError - index out of range errors"""
    
    def explain(self, exception: IndexError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет IndexError простыми словами
        
        Args:
            exception: IndexError для объяснения
            traceback_obj: Объект трассировки
            
        Returns:
            Человеко-читаемое объяснение
        """
        error_message = str(exception)
        
        # Получаем контекстную информацию
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        if self._get_language() == "ru":
            explanation = f"📊 {error_message}"
        else:
            explanation = f"📊 {error_message}"
        
        # Анализируем сообщение об ошибке
        if "list index out of range" in error_message:
            explanation = self._explain_list_index_error(locals_dict)
        elif "string index out of range" in error_message:
            explanation = self._explain_string_index_error(locals_dict)
        elif "tuple index out of range" in error_message:
            explanation = self._explain_tuple_index_error(locals_dict)
        else:
            explanation = f"📊 Выход за границы индекса: {error_message}"
        
        # Добавляем предложения
        suggestions = self.get_suggestions(exception)
        if suggestions:
            explanation += "\n\n🔧 Как исправить:"
            for i, suggestion in enumerate(suggestions, 1):
                explanation += f"\n{i}. {suggestion}"
        
        return explanation
    
    def _explain_list_index_error(self, locals_dict: dict) -> str:
        """Объясняет ошибки индексации списка / Explains list indexing errors"""
        # Ищем списки в локальных переменных
        lists_info = []
        for var_name, var_value in locals_dict.items():
            if isinstance(var_value, list):
                lists_info.append({
                    'name': var_name,
                    'length': len(var_value),
                    'items': var_value[:5]  # Первые 5 элементов
                })
        
        if lists_info:
            most_likely_list = lists_info[0]  # Берем первый список
            if self._get_language() == "ru":
                explanation = f"📊 Список '{most_likely_list['name']}' содержит {most_likely_list['length']} элементов"
                if most_likely_list['items']:
                    explanation += f"\n📋 Первые элементы: {most_likely_list['items']}"
                explanation += "\n💡 Индексы должны быть от 0 до " + str(most_likely_list['length'] - 1)
            else:
                explanation = f"📊 List '{most_likely_list['name']}' contains {most_likely_list['length']} elements"
                if most_likely_list['items']:
                    explanation += f"\n📋 First elements: {most_likely_list['items']}"
                explanation += "\n💡 Indices should be from 0 to " + str(most_likely_list['length'] - 1)
        else:
            if self._get_language() == "ru":
                explanation = "📊 Попытка обратиться к элементу списка по несуществующему индексу"
            else:
                explanation = "📊 Attempt to access list element with non-existent index"
        
        return explanation
    
    def _explain_string_index_error(self, locals_dict: dict) -> str:
        """Объясняет ошибки индексации строки"""
        # Ищем строки в локальных переменных
        strings_info = []
        for var_name, var_value in locals_dict.items():
            if isinstance(var_value, str):
                strings_info.append({
                    'name': var_name,
                    'length': len(var_value),
                    'preview': var_value[:20] + "..." if len(var_value) > 20 else var_value
                })
        
        if strings_info:
            most_likely_string = strings_info[0]
            explanation = f"📝 Строка '{most_likely_string['name']}' содержит {most_likely_string['length']} символов"
            explanation += f"\n📋 Содержимое: '{most_likely_string['preview']}'"
            explanation += "\n💡 Индексы должны быть от 0 до " + str(most_likely_string['length'] - 1)
        else:
            explanation = "📝 Попытка обратиться к символу строки по несуществующему индексу"
        
        return explanation
    
    def _explain_tuple_index_error(self, locals_dict: dict) -> str:
        """Объясняет ошибки индексации кортежа"""
        # Ищем кортежи в локальных переменных
        tuples_info = []
        for var_name, var_value in locals_dict.items():
            if isinstance(var_value, tuple):
                tuples_info.append({
                    'name': var_name,
                    'length': len(var_value),
                    'items': var_value[:5]  # Первые 5 элементов
                })
        
        if tuples_info:
            most_likely_tuple = tuples_info[0]
            explanation = f"📦 Кортеж '{most_likely_tuple['name']}' содержит {most_likely_tuple['length']} элементов"
            if most_likely_tuple['items']:
                explanation += f"\n📋 Элементы: {most_likely_tuple['items']}"
            explanation += "\n💡 Индексы должны быть от 0 до " + str(most_likely_tuple['length'] - 1)
        else:
            explanation = "📦 Попытка обратиться к элементу кортежа по несуществующему индексу"
        
        return explanation
    
    def get_suggestions(self, exception: IndexError) -> list[str]:
        """Возвращает предложения по исправлению IndexError / Returns suggestions for fixing IndexError"""
        if self._get_language() == "ru":
            return [
                "Проверьте длину последовательности перед обращением к элементу: len(sequence)",
                "Используйте безопасный доступ: sequence[i] if i < len(sequence) else default_value",
                "Проверьте, что индекс не отрицательный и не превышает длину",
                "Используйте try-except для обработки ошибок индексации",
                "Для списков используйте .append() вместо обращения по несуществующему индексу",
                "Проверьте, что последовательность не пустая перед обращением к элементам"
            ]
        else:
            return [
                "Check sequence length before accessing element: len(sequence)",
                "Use safe access: sequence[i] if i < len(sequence) else default_value",
                "Check that index is not negative and doesn't exceed length",
                "Use try-except to handle indexing errors",
                "For lists use .append() instead of accessing non-existent index",
                "Check that sequence is not empty before accessing elements"
            ]
