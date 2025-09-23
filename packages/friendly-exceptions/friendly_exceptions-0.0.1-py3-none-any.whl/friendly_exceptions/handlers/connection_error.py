"""
Обработчик для ConnectionError и связанных сетевых ошибок
ConnectionError and related network errors handler
"""

from typing import Optional, Any
from .base import BaseHandler


class ConnectionErrorHandler(BaseHandler):
    """Обработчик для ConnectionError - ошибок сетевого соединения
    Handler for ConnectionError - network connection errors"""
    
    def explain(self, exception: ConnectionError, traceback_obj: Optional[Any] = None) -> str:
        """
        Объясняет ConnectionError простыми словами
        Explains ConnectionError in simple terms
        
        Args:
            exception: ConnectionError для объяснения / ConnectionError to explain
            traceback_obj: Объект трассировки / Traceback object
            
        Returns:
            Человеко-читаемое объяснение / Human-readable explanation
        """
        error_message = str(exception)
        
        if self._get_language() == "ru":
            explanation = f"🌐 Ошибка сетевого соединения: {error_message}"
        else:
            explanation = f"🌐 Network connection error: {error_message}"
        
        # Анализируем тип ошибки
        if "Connection refused" in error_message:
            explanation = self._explain_connection_refused(error_message)
        elif "Connection timed out" in error_message:
            explanation = self._explain_connection_timeout(error_message)
        elif "Connection reset" in error_message:
            explanation = self._explain_connection_reset(error_message)
        elif "Connection aborted" in error_message:
            explanation = self._explain_connection_aborted(error_message)
        elif "Name or service not known" in error_message:
            explanation = self._explain_name_not_known(error_message)
        elif "Network is unreachable" in error_message:
            explanation = self._explain_network_unreachable(error_message)
        
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
    
    def _explain_connection_refused(self, error_message: str) -> str:
        """Объясняет ошибку 'соединение отклонено' / Explains 'connection refused' error"""
        if self._get_language() == "ru":
            return "🚫 Соединение отклонено сервером. Сервер может быть недоступен или не принимать подключения"
        else:
            return "🚫 Connection refused by server. Server may be unavailable or not accepting connections"
    
    def _explain_connection_timeout(self, error_message: str) -> str:
        """Объясняет ошибку таймаута / Explains timeout error"""
        if self._get_language() == "ru":
            return "⏰ Превышено время ожидания соединения. Сервер слишком долго не отвечает"
        else:
            return "⏰ Connection timeout exceeded. Server is taking too long to respond"
    
    def _explain_connection_reset(self, error_message: str) -> str:
        """Объясняет ошибку сброса соединения / Explains connection reset error"""
        if self._get_language() == "ru":
            return "🔄 Соединение было сброшено сервером во время передачи данных"
        else:
            return "🔄 Connection was reset by server during data transmission"
    
    def _explain_connection_aborted(self, error_message: str) -> str:
        """Объясняет ошибку прерывания соединения / Explains connection aborted error"""
        if self._get_language() == "ru":
            return "❌ Соединение было прервано. Возможно, проблема с сетью"
        else:
            return "❌ Connection was aborted. Possible network issue"
    
    def _explain_name_not_known(self, error_message: str) -> str:
        """Объясняет ошибку 'имя не найдено' / Explains 'name not known' error"""
        if self._get_language() == "ru":
            return "🔍 Не удалось найти сервер по указанному имени. Проверьте правильность адреса"
        else:
            return "🔍 Could not find server by the specified name. Check the address is correct"
    
    def _explain_network_unreachable(self, error_message: str) -> str:
        """Объясняет ошибку 'сеть недоступна' / Explains 'network unreachable' error"""
        if self._get_language() == "ru":
            return "📡 Сеть недоступна. Проверьте подключение к интернету"
        else:
            return "📡 Network is unreachable. Check your internet connection"
    
    def get_suggestions(self, exception: ConnectionError) -> list[str]:
        """Возвращает предложения по исправлению ConnectionError / Returns suggestions for fixing ConnectionError"""
        if self._get_language() == "ru":
            return [
                "Проверьте подключение к интернету",
                "Убедитесь, что сервер доступен и работает",
                "Проверьте правильность URL или адреса сервера",
                "Попробуйте увеличить таймаут соединения",
                "Проверьте настройки брандмауэра и прокси",
                "Попробуйте повторить запрос позже"
            ]
        else:
            return [
                "Check your internet connection",
                "Make sure the server is available and running",
                "Check the URL or server address is correct",
                "Try increasing the connection timeout",
                "Check firewall and proxy settings",
                "Try the request again later"
            ]
