"""
Обработчик для AttributeError
AttributeError handler
"""

import difflib
from typing import Optional, Any
from .base import BaseHandler


class AttributeErrorHandler(BaseHandler):
    """Обработчик для AttributeError - ошибок доступа к несуществующим атрибутам
    Handler for AttributeError - errors accessing non-existent attributes"""
    
    def explain(self, exception: AttributeError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет AttributeError простыми словами
        
        Args:
            exception: AttributeError для объяснения
            traceback_obj: Объект трассировки
            
        Returns:
            Человеко-читаемое объяснение
        """
        error_message = str(exception)
        
        # Получаем контекстную информацию
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        if self._get_language() == "ru":
            explanation = f"🔍 {error_message}"
        else:
            explanation = f"🔍 {error_message}"
        
        # Анализируем сообщение об ошибке
        if "'" in error_message and "has no attribute" in error_message:
            # Парсим сообщение вида "'Test' object has no attribute 'nmae'"
            parts = error_message.split("'")
            if len(parts) >= 4:
                # parts[0] = пустая строка
                # parts[1] = 'Test' (тип объекта)
                # parts[2] = ' object has no attribute '
                # parts[3] = 'nmae' (отсутствующий атрибут)
                object_type = parts[1]
                missing_attribute = parts[3]
                
                # Ищем объект в локальных переменных
                variable_name = self._find_object_in_locals(object_type, locals_dict)
                
                if variable_name:
                    if self._get_language() == "ru":
                        explanation = f"🔍 Переменная '{variable_name}' (тип '{object_type}') не имеет атрибута '{missing_attribute}'"
                    else:
                        explanation = f"🔍 Variable '{variable_name}' (type '{object_type}') has no attribute '{missing_attribute}'"
                else:
                    if self._get_language() == "ru":
                        explanation = f"🔍 Объект типа '{object_type}' не имеет атрибута '{missing_attribute}'"
                    else:
                        explanation = f"🔍 Object of type '{object_type}' has no attribute '{missing_attribute}'"
                
                # Ищем похожие атрибуты
                similar_attributes = self._find_similar_attributes(missing_attribute, object_type, locals_dict)
                if similar_attributes:
                    if self._get_language() == "ru":
                        explanation += f"\n💡 Возможно, вы имели в виду: {similar_attributes}"
                    else:
                        explanation += f"\n💡 Perhaps you meant: {similar_attributes}"
                
                # Добавляем информацию о типе объекта
                if self._get_language() == "ru":
                    explanation += f"\n📋 Тип объекта: {object_type}"
                else:
                    explanation += f"\n📋 Object type: {object_type}"
            else:
                # Если не удалось разобрать, используем общее объяснение
                if self._get_language() == "ru":
                    explanation = f"🔍 {error_message}"
                else:
                    explanation = f"🔍 {error_message}"
        else:
            # Если не удалось разобрать сообщение, используем общее объяснение
            if self._get_language() == "ru":
                explanation = f"🔍 {error_message}"
            else:
                explanation = f"🔍 {error_message}"
        
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
    
    def _find_object_in_locals(self, object_type: str, locals_dict: dict) -> Optional[str]:
        """
        Ищет объект указанного типа в локальных переменных
        
        Args:
            object_type: Тип объекта для поиска
            locals_dict: Словарь локальных переменных
            
        Returns:
            Имя переменной или None, если не найдено
        """
        for var_name, var_value in locals_dict.items():
            if hasattr(var_value, '__class__') and var_value.__class__.__name__ == object_type:
                return var_name
        return None
    
    def _find_similar_attributes(self, target_attribute: str, object_type: str, locals_dict: dict = None) -> list[str]:
        """
        Находит атрибуты, похожие на целевой
        
        Args:
            target_attribute: Искомый атрибут
            object_type: Тип объекта
            locals_dict: Словарь локальных переменных
            
        Returns:
            Список похожих атрибутов
        """
        # Сначала пытаемся найти реальный объект в локальных переменных
        if locals_dict:
            for var_name, var_value in locals_dict.items():
                if hasattr(var_value, '__class__') and var_value.__class__.__name__ == object_type:
                    # Используем реальные атрибуты объекта
                    try:
                        real_attributes = dir(var_value)
                        # Используем difflib для поиска похожих атрибутов
                        similar = difflib.get_close_matches(target_attribute, real_attributes, n=3, cutoff=0.6)
                        if similar:
                            return similar
                    except Exception:
                        pass
        
        # Если не нашли реальный объект, используем базовые атрибуты
        common_attributes = {
            'str': ['upper', 'lower', 'strip', 'split', 'replace', 'find', 'index', 'count', 'startswith', 'endswith'],
            'list': ['append', 'extend', 'insert', 'remove', 'pop', 'index', 'count', 'sort', 'reverse', 'clear'],
            'dict': ['keys', 'values', 'items', 'get', 'pop', 'update', 'clear', 'copy'],
            'int': ['bit_length', 'to_bytes', 'from_bytes'],
            'float': ['is_integer', 'as_integer_ratio', 'hex', 'fromhex'],
            'tuple': ['index', 'count'],
            'set': ['add', 'remove', 'discard', 'pop', 'clear', 'copy', 'union', 'intersection', 'difference'],
        }
        
        # Получаем возможные атрибуты для данного типа
        possible_attributes = common_attributes.get(object_type.lower(), [])
        
        # Используем difflib для поиска похожих атрибутов
        similar = difflib.get_close_matches(target_attribute, possible_attributes, n=3, cutoff=0.6)
        
        if not similar:
            # Если difflib не нашел похожих, используем старый алгоритм
            similar = []
            target_lower = target_attribute.lower()
            
            for attr in possible_attributes:
                attr_lower = attr.lower()
                
                # Точное совпадение (разный регистр)
                if attr_lower == target_lower and attr != target_attribute:
                    similar.append(attr)
                # Содержит целевой атрибут
                elif target_lower in attr_lower or attr_lower in target_lower:
                    similar.append(attr)
                # Начинается с того же
                elif attr_lower.startswith(target_lower[:3]) or target_lower.startswith(attr_lower[:3]):
                    similar.append(attr)
        
        return similar[:3]  # Возвращаем максимум 3 похожих атрибута
    
    def get_suggestions(self, exception: AttributeError) -> list[str]:
        """Возвращает предложения по исправлению AttributeError / Returns suggestions for fixing AttributeError"""
        error_message = str(exception)
        
        if "'" in error_message and "has no attribute" in error_message:
            if self._get_language() == "ru":
                return [
                    "Проверьте правильность написания имени атрибута",
                    "Убедитесь, что объект имеет нужный атрибут: hasattr(obj, 'attr')",
                    "Используйте dir(obj) для просмотра всех доступных атрибутов",
                    "Проверьте, что объект инициализирован правильно",
                    "Убедитесь, что используете правильный тип объекта"
                ]
            else:
                return [
                    "Check the spelling of the attribute name",
                    "Make sure the object has the required attribute: hasattr(obj, 'attr')",
                    "Use dir(obj) to view all available attributes",
                    "Check that the object is properly initialized",
                    "Make sure you're using the correct object type"
                ]
        else:
            if self._get_language() == "ru":
                return [
                    "Проверьте, что объект существует и инициализирован",
                    "Убедитесь, что атрибут доступен для данного типа объекта",
                    "Используйте getattr() для безопасного доступа к атрибутам",
                    "Проверьте документацию по используемому классу или модулю"
                ]
            else:
                return [
                    "Check that the object exists and is initialized",
                    "Make sure the attribute is available for this object type",
                    "Use getattr() for safe attribute access",
                    "Check the documentation for the class or module you're using"
                ]
