"""
Обработчик для RuntimeError
RuntimeError handler
"""

from typing import Optional, Any
from .base import BaseHandler


class RuntimeErrorHandler(BaseHandler):
    """Обработчик для RuntimeError - ошибок времени выполнения
    Handler for RuntimeError - runtime errors"""
    
    def explain(self, exception: RuntimeError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет RuntimeError простыми словами
        Explains RuntimeError in simple terms
        
        Args:
            exception: RuntimeError для объяснения / RuntimeError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"⚡ Ошибка времени выполнения: {error_message}"
        else:
            explanation = f"⚡ Runtime error: {error_message}"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем информацию о состоянии программы
        state_info = self._analyze_program_state(locals_dict)
        if state_info:
            if self._get_language() == "ru":
                explanation += f"\n📊 Состояние программы: {state_info}"
            else:
                explanation += f"\n📊 Program state: {state_info}"
        
        # Анализируем тип ошибки
        if "maximum recursion depth exceeded" in error_message.lower():
            explanation = self._explain_recursion_depth(error_message)
        elif "cannot be used in a constant expression" in error_message.lower():
            explanation = self._explain_constant_expression(error_message)
        elif "generator didn't stop" in error_message.lower():
            explanation = self._explain_generator_error(error_message)
        elif "cannot be used in a constant expression" in error_message.lower():
            explanation = self._explain_constant_expression(error_message)
        
        # Объясняем проблему
        if self._get_language() == "ru":
            explanation += "\n💡 Произошла ошибка во время выполнения программы"
        else:
            explanation += "\n💡 An error occurred during program execution"
        
        # Добавляем ссылку на документацию
        if self._get_language() == "ru":
            explanation += "\n\n📚 Документация: https://docs.python.org/3/library/exceptions.html#RuntimeError"
        else:
            explanation += "\n\n📚 Documentation: https://docs.python.org/3/library/exceptions.html#RuntimeError"
        
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
    
    def _analyze_program_state(self, locals_dict: dict) -> Optional[str]:
        """Анализирует состояние программы / Analyzes program state"""
        state_info = []
        
        for var_name, var_value in locals_dict.items():
            if not var_name.startswith('__'):
                if isinstance(var_value, (int, float, str, bool)):
                    state_info.append(f"{var_name}={var_value}")
                elif hasattr(var_value, '__len__'):
                    state_info.append(f"{var_name}(len={len(var_value)})")
        
        return ", ".join(state_info[:3]) if state_info else None
    
    def _explain_recursion_depth(self, error_message: str) -> str:
        """Объясняет ошибку глубины рекурсии / Explains recursion depth error"""
        if self._get_language() == "ru":
            return "🔄 Превышена максимальная глубина рекурсии. Функция вызывает сама себя слишком много раз"
        else:
            return "🔄 Maximum recursion depth exceeded. Function calls itself too many times"
    
    def _explain_constant_expression(self, error_message: str) -> str:
        """Объясняет ошибку константного выражения / Explains constant expression error"""
        if self._get_language() == "ru":
            return "📝 Нельзя использовать в константном выражении. Переменная должна быть константой"
        else:
            return "📝 Cannot be used in a constant expression. Variable must be a constant"
    
    def _explain_generator_error(self, error_message: str) -> str:
        """Объясняет ошибку генератора / Explains generator error"""
        if self._get_language() == "ru":
            return "🔄 Генератор не остановился. Возможно, бесконечный цикл в генераторе"
        else:
            return "🔄 Generator didn't stop. Possible infinite loop in generator"
    
    def get_suggestions(self, exception: RuntimeError) -> list[str]:
        """Возвращает предложения по исправлению RuntimeError / Returns suggestions for fixing RuntimeError"""
        error_message = str(exception)
        
        if "maximum recursion depth exceeded" in error_message.lower():
            if self._get_language() == "ru":
                return [
                    "Добавьте базовый случай для остановки рекурсии",
                    "Используйте итеративный подход вместо рекурсии",
                    "Увеличьте лимит рекурсии: sys.setrecursionlimit(2000)",
                    "Проверьте, что рекурсивный вызов приближает к базовому случаю"
                ]
            else:
                return [
                    "Add a base case to stop recursion",
                    "Use iterative approach instead of recursion",
                    "Increase recursion limit: sys.setrecursionlimit(2000)",
                    "Check that recursive call approaches the base case"
                ]
        else:
            if self._get_language() == "ru":
                return [
                    "Проверьте логику программы в месте ошибки",
                    "Убедитесь, что все переменные определены",
                    "Проверьте входные данные на корректность",
                    "Используйте отладку для пошагового выполнения",
                    "Проверьте, что нет бесконечных циклов",
                    "Убедитесь, что ресурсы освобождаются правильно"
                ]
            else:
                return [
                    "Check program logic at the error location",
                    "Make sure all variables are defined",
                    "Check input data for correctness",
                    "Use debugging for step-by-step execution",
                    "Check that there are no infinite loops",
                    "Make sure resources are properly released"
                ]
