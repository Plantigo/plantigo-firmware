import json
import uos
import logging
from utils import file_exists

logger = logging.getLogger("ConfigManager")


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Ładuje konfigurację z pliku, lub tworzy domyślną jeśli plik nie istnieje"""
        self.default_config = {
            "data_storage": {
                "sensor_data_filename": "sensor_data.bin",
                "max_days_to_keep": 7,
                "sampling_rate": {
                    "day_start_hour": 6,  # Godzina rozpoczęcia trybu dziennego
                    "day_end_hour": 22,  # Godzina zakończenia trybu dziennego
                    "day_interval": 300,  # Interwał w sekundach (5 minut) w dzień
                    "night_interval": 1800  # Interwał w sekundach (30 minut) w nocy
                }
            },
            "sampling": {
                "mqtt_publish_interval": 5,
                "sensor_read_interval": 5
            },
            "web_server": {
                "port": 80,
                "debug": True
            },
            "sensors": {
                "temperature_precision": 2,
                "humidity_precision": 2,
                "soil_moisture_precision": 1,
                "light_precision": 1
            }
        }

        try:
            if file_exists('config.json'):
                try:
                    with open('config.json', 'r') as f:
                        content = f.read()
                    # Usuń wszystkie białe znaki i nowe linie dla większej kompatybilności
                    content = ''.join(content.split())
                    self.config = json.loads(content)
                    logger.info("Załadowano konfigurację z pliku config.json")
                except ValueError as e:
                    logger.error(f"Błąd parsowania JSON: {e}")
                    self.config = self.default_config
                    self._save_config()  # Nadpisz uszkodzony plik poprawną konfiguracją
                    logger.info("Utworzono nową domyślną konfigurację z powodu błędu w pliku")
            else:
                self.config = self.default_config
                self._save_config()
                logger.info("Utworzono domyślną konfigurację")
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
            self.config = self.default_config

    def _save_config(self):
        """Zapisuje aktualną konfigurację do pliku"""
        try:
            with open('config.json', 'w') as f:
                # Zapisz w jednej linii bez wcięć dla większej kompatybilności
                json.dump(self.config, f, separators=(',', ':'))
            logger.info("Zapisano konfigurację do pliku config.json")
        except Exception as e:
            logger.error(f"Błąd podczas zapisu konfiguracji: {e}")

    def get(self, section, key, default=None):
        """Pobiera wartość z konfiguracji"""
        try:
            return self.config[section][key]
        except KeyError:
            if default is not None:
                return default
            return self.default_config[section][key]

    def set(self, section, key, value):
        """Ustawia wartość w konfiguracji i zapisuje do pliku"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config()

    def get_all(self):
        """Zwraca całą konfigurację"""
        return self.config


# Singleton instance
config = ConfigManager()
