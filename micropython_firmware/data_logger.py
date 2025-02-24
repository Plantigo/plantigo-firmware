import uos as os
import time
import struct
import logging
from config_manager import config
from data_compression import block_manager

logger = logging.getLogger("DataLogger")


class DataLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.current_block = []
            self.last_save_time = time.time()
            self.initialized = True

    def get_current_interval(self):
        """Określa aktualny interwał próbkowania na podstawie pory dnia"""
        current_hour = time.localtime()[3]  # indeks 3 to godzina
        day_start = config.get('data_storage', 'sampling_rate')['day_start_hour']
        day_end = config.get('data_storage', 'sampling_rate')['day_end_hour']

        if day_start <= current_hour < day_end:
            return config.get('data_storage', 'sampling_rate')['day_interval']
        return config.get('data_storage', 'sampling_rate')['night_interval']

    def pack_record(self, data):
        """Pakuje dane do formatu binarnego"""
        try:
            return struct.pack(
                '>dffff',  # > - big endian, d - double (timestamp), f - float
                data['timestamp'],
                data['temperature'] if data['temperature'] is not None else -999.9,
                data['humidity'] if data['humidity'] is not None else -999.9,
                data['soil_moisture'] if data['soil_moisture'] is not None else -999.9,
                data['light'] if data['light'] is not None else -999.9
            )
        except Exception as e:
            logger.error(f"Błąd pakowania danych: {e}")
            return None

    def save_data(self, data):
        """Zapisuje nowe dane z uwzględnieniem kompresji"""
        try:
            # Sprawdź czy powinniśmy zapisać dane (na podstawie interwału)
            current_time = time.time()
            if current_time - self.last_save_time < self.get_current_interval():
                return

            self.last_save_time = current_time

            # Pakuj dane do formatu binarnego
            record = self.pack_record(data)
            if not record:
                return

            # Dodaj do aktualnego bloku
            self.current_block.append(record)

            # Jeśli blok jest pełny, zapisz go
            if len(self.current_block) >= block_manager.compressor.BLOCK_SIZE:
                block_manager.save_block(self.current_block, current_time)
                self.current_block = []

            # Usuń stare bloki
            max_days = config.get('data_storage', 'max_days_to_keep')
            block_manager.cleanup_old_blocks(max_days)

        except Exception as e:
            logger.error(f"Błąd podczas zapisu danych: {e}")

    def get_data(self, hours=24):
        """Pobiera dane z określonego okresu"""
        try:
            result = []
            current_time = time.time()
            start_time = current_time - (hours * 3600)

            # Pobierz wszystkie potrzebne bloki
            for hour in range(int(start_time // 3600), int(current_time // 3600) + 1):
                records = block_manager.load_block(hour * 3600)
                for record in records:
                    # Rozpakuj rekord
                    timestamp, temp, hum, soil, light = struct.unpack('>dffff', record)

                    # Sprawdź czy rekord jest z zadanego okresu
                    if start_time <= timestamp <= current_time:
                        # Zastosuj precyzję z konfiguracji
                        temp_precision = config.get('sensors', 'temperature_precision')
                        hum_precision = config.get('sensors', 'humidity_precision')
                        soil_precision = config.get('sensors', 'soil_moisture_precision')
                        light_precision = config.get('sensors', 'light_precision')

                        data = {
                            "timestamp": timestamp,
                            "temperature": round(temp, temp_precision) if temp > -999 else None,
                            "humidity": round(hum, hum_precision) if hum > -999 else None,
                            "soil_moisture": round(soil, soil_precision) if soil > -999 else None,
                            "light": round(light, light_precision) if light > -999 else None
                        }
                        result.append(data)

            # Dodaj dane z aktualnego bloku
            for record in self.current_block:
                timestamp, temp, hum, soil, light = struct.unpack('>dffff', record)
                if start_time <= timestamp <= current_time:
                    data = {
                        "timestamp": timestamp,
                        "temperature": round(temp, temp_precision) if temp > -999 else None,
                        "humidity": round(hum, hum_precision) if hum > -999 else None,
                        "soil_moisture": round(soil, soil_precision) if soil > -999 else None,
                        "light": round(light, light_precision) if light > -999 else None
                    }
                    result.append(data)

            return sorted(result, key=lambda x: x['timestamp'])

        except Exception as e:
            logger.error(f"Błąd podczas odczytu danych: {e}")
            return []


# Singleton instance
data_logger = DataLogger()
