"""
Обработчик для MemoryError
MemoryError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class MemoryErrorHandler(BaseHandler):
    """Обработчик для MemoryError - ошибок памяти
    Handler for MemoryError - memory errors"""
    
    def explain(self, exception: MemoryError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет MemoryError простыми словами
        Explains MemoryError in simple terms
        
        Args:
            exception: MemoryError для объяснения / MemoryError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"💾 Ошибка памяти: {error_message}"
        else:
            explanation = f"💾 Memory error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем большие объекты в контексте
        large_objects = self._find_large_objects(locals_dict)
        if large_objects:
            if self._get_language() == "ru":
                explanation += f"\n📊 Большие объекты: {large_objects}"
            else:
                explanation += f"\n📊 Large objects: {large_objects}"
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Недостаточно оперативной памяти для выполнения операции"
        else:
            explanation += "\n💡 Not enough RAM to perform the operation"
        
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
    
    def _find_large_objects(self, locals_dict: dict) -> Optional[str]:
        """Ищет большие объекты в контексте / Finds large objects in context"""
        large_objects = []
        
        for var_name, var_value in locals_dict.items():
            try:
                # Проверяем размер объекта
                size = len(var_value) if hasattr(var_value, '__len__') else 0
                if size > 1000000:  # Больше 1 миллиона элементов
                    large_objects.append(f"{var_name}({size} элементов)")
            except:
                pass
        
        return ", ".join(large_objects) if large_objects else None
    
    def get_suggestions(self, exception: MemoryError) -> list[str]:
        """Возвращает предложения по исправлению MemoryError / Returns suggestions for fixing MemoryError"""
        if self._get_language() == "ru":
            return [
                "Обрабатывайте данные по частям (chunking)",
                "Используйте генераторы вместо списков для больших данных",
                "Удаляйте ненужные переменные: del variable_name",
                "Используйте numpy для эффективной работы с массивами",
                "Рассмотрите использование базы данных для больших данных",
                "Увеличьте объем оперативной памяти",
                "Используйте сборщик мусора: gc.collect()"
            ]
        else:
            return [
                "Process data in chunks",
                "Use generators instead of lists for large data",
                "Delete unnecessary variables: del variable_name",
                "Use numpy for efficient array operations",
                "Consider using a database for large data",
                "Increase RAM capacity",
                "Use garbage collector: gc.collect()"
            ]
