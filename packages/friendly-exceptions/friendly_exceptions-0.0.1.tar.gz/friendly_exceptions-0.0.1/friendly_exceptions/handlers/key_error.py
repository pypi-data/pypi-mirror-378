"""
Обработчик для KeyError
KeyError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class KeyErrorHandler(BaseHandler):
    """Обработчик для KeyError - ошибок доступа к несуществующим ключам словаря
    Handler for KeyError - errors accessing non-existent dictionary keys"""
    
    def explain(self, exception: KeyError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет KeyError простыми словами
        
        Args:
            exception: KeyError для объяснения
            traceback_obj: Объект трассировки
            
        Returns:
            Человеко-читаемое объяснение
        """
        missing_key = str(exception)
        
        # Получаем контекстную информацию
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем словари в локальных переменных (исключая служебные)
        dicts_info = []
        for var_name, var_value in locals_dict.items():
            # Пропускаем служебные переменные Python
            if var_name.startswith('__') and var_name.endswith('__'):
                continue
            
            if isinstance(var_value, dict):
                dicts_info.append({
                    'name': var_name,
                    'keys': list(var_value.keys()),
                    'size': len(var_value)
                })
        
        # Формируем объяснение
        if self._get_language() == "ru":
            explanation = f"🔑 Словарь не содержит ключ '{missing_key}'"
        else:
            explanation = f"🔑 Dictionary does not contain key '{missing_key}'"
        
        if dicts_info:
            # Находим наиболее вероятный словарь
            most_likely_dict = None
            
            # Сначала ищем словари с похожими ключами
            for dict_info in dicts_info:
                if missing_key in dict_info['keys']:
                    continue  # Ключ есть, это не тот словарь
                
                # Проверяем на похожие ключи
                similar_keys = self._find_similar_keys(missing_key, dict_info['keys'])
                if similar_keys:
                    most_likely_dict = dict_info
                    break
            
            # Если не нашли с похожими ключами, берем самый большой словарь
            if not most_likely_dict and dicts_info:
                # Сортируем по размеру (большие словари приоритетнее)
                dicts_info.sort(key=lambda x: x['size'], reverse=True)
                most_likely_dict = dicts_info[0]
            
            if most_likely_dict:
                if self._get_language() == "ru":
                    explanation += f"\n📋 В словаре '{most_likely_dict['name']}' доступны ключи: {most_likely_dict['keys']}"
                else:
                    explanation += f"\n📋 Dictionary '{most_likely_dict['name']}' contains keys: {most_likely_dict['keys']}"
                
                # Ищем похожие ключи
                similar_keys = self._find_similar_keys(missing_key, most_likely_dict['keys'])
                if similar_keys:
                    if self._get_language() == "ru":
                        explanation += f"\n💡 Возможно, вы имели в виду: {similar_keys}"
                    else:
                        explanation += f"\n💡 Perhaps you meant: {similar_keys}"
        
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
    
    def get_suggestions(self, exception: KeyError) -> list[str]:
        """Возвращает предложения по исправлению KeyError / Returns suggestions for fixing KeyError"""
        if self._get_language() == "ru":
            return [
                "Проверьте правильность написания ключа",
                "Убедитесь, что ключ существует в словаре перед обращением",
                "Используйте метод .get() для безопасного доступа: dict.get('key', default_value)",
                "Проверьте, что словарь не пустой: if dict: ...",
                "Используйте 'key' in dict для проверки существования ключа"
            ]
        else:
            return [
                "Check the spelling of the key",
                "Make sure the key exists in the dictionary before accessing it",
                "Use .get() method for safe access: dict.get('key', default_value)",
                "Check that the dictionary is not empty: if dict: ...",
                "Use 'key' in dict to check if key exists"
            ]
    
    def _find_similar_keys(self, target_key: str, available_keys: list[str]) -> list[str]:
        """
        Находит ключи, похожие на целевой
        
        Args:
            target_key: Искомый ключ
            available_keys: Доступные ключи
            
        Returns:
            Список похожих ключей
        """
        similar = []
        target_lower = target_key.lower()
        
        for key in available_keys:
            key_lower = key.lower()
            
            # Точное совпадение (разный регистр)
            if key_lower == target_lower and key != target_key:
                similar.append(key)
            # Содержит целевой ключ
            elif target_lower in key_lower or key_lower in target_lower:
                similar.append(key)
            # Начинается с того же
            elif key_lower.startswith(target_lower[:3]) or target_lower.startswith(key_lower[:3]):
                similar.append(key)
        
        return similar[:3]  # Возвращаем максимум 3 похожих ключа
