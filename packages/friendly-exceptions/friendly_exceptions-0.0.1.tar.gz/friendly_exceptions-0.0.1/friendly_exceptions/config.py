"""
Система конфигурации для friendly_exceptions
Configuration system for friendly_exceptions
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Класс для управления конфигурацией / Configuration management class"""
    
    def __init__(self):
        self._config = {
            "language": "ru",
            "show_original_traceback": True,
            "show_suggestions": True,
            "max_suggestions": 5,
            "enable_colors": True,
            "log_level": "INFO",
            "log_file": None,
        }
        self._config_file = self._get_config_file_path()
        self._load_config()
    
    def _get_config_file_path(self) -> Path:
        """Получает путь к файлу конфигурации / Gets config file path"""
        # Ищем в текущей директории, затем в домашней
        current_dir = Path.cwd() / ".friendly_exceptions.json"
        home_dir = Path.home() / ".friendly_exceptions.json"
        
        if current_dir.exists():
            return current_dir
        return home_dir
    
    def _load_config(self):
        """Загружает конфигурацию из файла / Loads config from file"""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
            except (json.JSONDecodeError, IOError):
                # Если файл поврежден, используем значения по умолчанию
                pass
        
        # Переопределяем переменными окружения
        self._load_from_env()
    
    def _load_from_env(self):
        """Загружает настройки из переменных окружения / Loads settings from environment variables"""
        env_mapping = {
            "FRIENDLY_EXCEPTIONS_LANGUAGE": "language",
            "FRIENDLY_EXCEPTIONS_SHOW_TRACEBACK": "show_original_traceback",
            "FRIENDLY_EXCEPTIONS_SHOW_SUGGESTIONS": "show_suggestions",
            "FRIENDLY_EXCEPTIONS_MAX_SUGGESTIONS": "max_suggestions",
            "FRIENDLY_EXCEPTIONS_ENABLE_COLORS": "enable_colors",
            "FRIENDLY_EXCEPTIONS_LOG_LEVEL": "log_level",
            "FRIENDLY_EXCEPTIONS_LOG_FILE": "log_file",
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Преобразуем строковые значения в нужные типы
                if config_key in ["show_original_traceback", "show_suggestions", "enable_colors"]:
                    self._config[config_key] = value.lower() in ("true", "1", "yes", "on")
                elif config_key in ["max_suggestions"]:
                    try:
                        self._config[config_key] = int(value)
                    except ValueError:
                        pass
                else:
                    self._config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получает значение конфигурации / Gets config value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Устанавливает значение конфигурации / Sets config value"""
        self._config[key] = value
    
    def save(self):
        """Сохраняет конфигурацию в файл / Saves config to file"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError:
            # Если не удается сохранить, игнорируем ошибку
            pass
    
    def reset(self):
        """Сбрасывает конфигурацию к значениям по умолчанию / Resets config to defaults"""
        self._config = {
            "language": "ru",
            "show_original_traceback": True,
            "show_suggestions": True,
            "max_suggestions": 5,
            "enable_colors": True,
            "log_level": "INFO",
            "log_file": None,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Возвращает конфигурацию как словарь / Returns config as dictionary"""
        return self._config.copy()
    
    def update(self, config_dict: Dict[str, Any]):
        """Обновляет конфигурацию из словаря / Updates config from dictionary"""
        self._config.update(config_dict)


# Глобальный экземпляр конфигурации
# Global config instance
config = Config()


def get_config() -> Config:
    """Получает глобальную конфигурацию / Gets global config"""
    return config


def set_config(key: str, value: Any):
    """Устанавливает значение конфигурации / Sets config value"""
    config.set(key, value)


def get_config_value(key: str, default: Any = None) -> Any:
    """Получает значение конфигурации / Gets config value"""
    return config.get(key, default)


def save_config():
    """Сохраняет конфигурацию / Saves config"""
    config.save()


def reset_config():
    """Сбрасывает конфигурацию / Resets config"""
    config.reset()
