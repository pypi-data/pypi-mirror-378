"""
Обработчик для NameError
NameError handler
"""

import difflib
from typing import Optional, Any
from .base import BaseHandler


class NameErrorHandler(BaseHandler):
    """Обработчик для NameError - ошибок неопределенных переменных
    Handler for NameError - undefined variable errors"""
    
    def explain(self, exception: NameError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет NameError простыми словами
        Explains NameError in simple terms
        
        Args:
            exception: NameError для объяснения / NameError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"🏷️ Ошибка имени: {error_message}"
        else:
            explanation = f"🏷️ Name error: {error_message}"
        
        # Извлекаем имя переменной из сообщения об ошибке
        variable_name = self._extract_variable_name(error_message)
        if variable_name:
            if self._get_language() == "ru":
                explanation += f"\n🔍 Неопределенная переменная: '{variable_name}'"
            else:
                explanation += f"\n🔍 Undefined variable: '{variable_name}'"
        
        # Анализируем контекст
        context = self.get_context_info(traceback_obj)
        locals_dict = context.get('locals', {})
        
        # Ищем похожие переменные
        similar_variables = self._find_similar_variables(variable_name, locals_dict)
        if similar_variables:
            if self._get_language() == "ru":
                explanation += f"\n💡 Возможно, вы имели в виду: {similar_variables}"
            else:
                explanation += f"\n💡 Perhaps you meant: {similar_variables}"
        
        # Анализируем тип ошибки
        if "is not defined" in error_message:
            explanation = self._explain_not_defined(error_message, variable_name)
        elif "is not defined in this scope" in error_message:
            explanation = self._explain_scope_error(error_message, variable_name)
        
        # Добавляем ссылку на документацию
        if self._get_language() == "ru":
            explanation += "\n\n📚 Документация: https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces"
        else:
            explanation += "\n\n📚 Documentation: https://docs.python.org/3/tutorial/classes.html#python-scopes-and-namespaces"
        
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
    
    def _extract_variable_name(self, error_message: str) -> Optional[str]:
        """Извлекает имя переменной из сообщения об ошибке / Extracts variable name from error message"""
        # "name 'variable_name' is not defined"
        if "'" in error_message:
            parts = error_message.split("'")
            if len(parts) >= 2:
                return parts[1]
        return None
    
    def _find_similar_variables(self, target_name: str, locals_dict: dict) -> list[str]:
        """Ищет похожие переменные в контексте / Finds similar variables in context"""
        if not target_name:
            return []
        
        available_names = []
        for var_name in locals_dict.keys():
            if not var_name.startswith('__'):
                available_names.append(var_name)
        
        # Добавляем встроенные функции и модули
        import builtins
        available_names.extend(dir(builtins))
        
        similar = difflib.get_close_matches(target_name, available_names, n=3, cutoff=0.6)
        return similar
    
    def _explain_not_defined(self, error_message: str, variable_name: Optional[str]) -> str:
        """Объясняет ошибку 'не определена' / Explains 'not defined' error"""
        if self._get_language() == "ru":
            return f"❌ Переменная '{variable_name}' не была определена перед использованием"
        else:
            return f"❌ Variable '{variable_name}' was not defined before use"
    
    def _explain_scope_error(self, error_message: str, variable_name: Optional[str]) -> str:
        """Объясняет ошибку области видимости / Explains scope error"""
        if self._get_language() == "ru":
            return f"🔍 Переменная '{variable_name}' не определена в текущей области видимости"
        else:
            return f"🔍 Variable '{variable_name}' is not defined in the current scope"
    
    def get_suggestions(self, exception: NameError) -> list[str]:
        """Возвращает предложения по исправлению NameError / Returns suggestions for fixing NameError"""
        if self._get_language() == "ru":
            return [
                "Определите переменную перед использованием: variable_name = value",
                "Проверьте правильность написания имени переменной",
                "Убедитесь, что переменная определена в правильной области видимости",
                "Используйте global для доступа к глобальным переменным",
                "Проверьте, что импортировали нужные модули",
                "Используйте dir() для просмотра доступных переменных",
                "Проверьте, что переменная не была удалена с помощью del"
            ]
        else:
            return [
                "Define the variable before using it: variable_name = value",
                "Check the spelling of the variable name",
                "Make sure the variable is defined in the correct scope",
                "Use global to access global variables",
                "Check that you imported the necessary modules",
                "Use dir() to view available variables",
                "Check that the variable wasn't deleted with del"
            ]
