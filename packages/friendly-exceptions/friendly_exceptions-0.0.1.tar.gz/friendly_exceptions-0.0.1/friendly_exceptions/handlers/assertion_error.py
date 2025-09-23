"""
Обработчик для AssertionError
AssertionError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class AssertionErrorHandler(BaseHandler):
    """Обработчик для AssertionError - ошибок утверждений
    Handler for AssertionError - assertion errors"""
    
    def explain(self, exception: AssertionError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет AssertionError простыми словами
        Explains AssertionError in simple terms
        
        Args:
            exception: AssertionError для объяснения / AssertionError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"⚠️ Ошибка утверждения: {error_message}"
        else:
            explanation = f"⚠️ Assertion error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем переменные в контексте assert
        assert_vars = self._find_assert_variables(locals_dict)
        if assert_vars:
            if self._get_language() == "ru":
                explanation += f"\n📊 Переменные в утверждении: {assert_vars}"
            else:
                explanation += f"\n📊 Variables in assertion: {assert_vars}"
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Утверждение (assert) вернуло False, что означает неожиданное состояние программы"
        else:
            explanation += "\n💡 The assertion (assert) returned False, indicating an unexpected program state"
        
        # Добавляем информацию о том, что такое assert
        if self._get_language() == "ru":
            explanation += "\n\n📝 assert используется для проверки условий, которые должны быть истинными"
        else:
            explanation += "\n\n📝 assert is used to check conditions that should be true"
        
        # Добавляем ссылку на документацию
        if self._get_language() == "ru":
            explanation += "\n📚 Документация: https://docs.python.org/3/reference/simple_stmts.html#assert"
        else:
            explanation += "\n📚 Documentation: https://docs.python.org/3/reference/simple_stmts.html#assert"
        
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
    
    def _find_assert_variables(self, locals_dict: dict) -> list[str]:
        """Ищет переменные, связанные с assert / Finds variables related to assert"""
        assert_vars = []
        
        for var_name, var_value in locals_dict.items():
            if not var_name.startswith('__'):
                # Добавляем переменные, которые могут быть связаны с assert
                if isinstance(var_value, (int, float, str, bool, list, dict, tuple)):
                    assert_vars.append(f"{var_name}={var_value}")
        
        return assert_vars[:5]  # Ограничиваем количество
    
    def get_suggestions(self, exception: AssertionError) -> list[str]:
        """Возвращает предложения по исправлению AssertionError / Returns suggestions for fixing AssertionError"""
        if self._get_language() == "ru":
            return [
                "Проверьте логику условия в assert",
                "Убедитесь, что все переменные в assert определены и имеют ожидаемые значения",
                "Добавьте отладочную информацию: assert condition, f'Debug info: {variable}'",
                "Проверьте, что входные данные соответствуют ожиданиям",
                "Рассмотрите использование try-except вместо assert для обработки ошибок",
                "Используйте assert только для отладки, не для обработки ошибок в продакшене",
                "Проверьте, что assert не отключен флагом -O"
            ]
        else:
            return [
                "Check the logic of the condition in assert",
                "Make sure all variables in assert are defined and have expected values",
                "Add debug information: assert condition, f'Debug info: {variable}'",
                "Check that input data meets expectations",
                "Consider using try-except instead of assert for error handling",
                "Use assert only for debugging, not for error handling in production",
                "Check that assert is not disabled by -O flag"
            ]
