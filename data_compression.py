import zlib
import struct
import time
import logging
import uos as os  # Zmiana na uos

logger = logging.getLogger("DataCompression")


class DataCompressor:
    def __init__(self):
        self.BLOCK_SIZE = 100  # Liczba rekordów w jednym bloku kompresji

    def compress_block(self, records):
        """Kompresuje blok danych używając DEFLATE"""
        try:
            # Konwertuj rekordy na bytes
            raw_data = b''.join(records)
            # Kompresuj
            compressor = zlib.compressobj()
            compressed = compressor.compress(raw_data)
            compressed += compressor.flush()
            return compressed
        except Exception as e:
            logger.error(f"Błąd kompresji: {e}")
            return None

    def decompress_block(self, compressed_data):
        """Dekompresuje blok danych"""
        try:
            # Dekompresuj
            decompressor = zlib.decompressobj()
            decompressed = decompressor.decompress(compressed_data)
            decompressed += decompressor.flush()
            # Podziel na rekordy
            record_size = 24  # rozmiar pojedynczego rekordu
            records = []
            for i in range(0, len(decompressed), record_size):
                records.append(decompressed[i:i + record_size])
            return records
        except Exception as e:
            logger.error(f"Błąd dekompresji: {e}")
            return []


class DataBlockManager:
    def __init__(self, filename_prefix="data_block_"):
        self.filename_prefix = filename_prefix
        self.compressor = DataCompressor()

    def get_block_filename(self, timestamp):
        """Generuje nazwę pliku dla bloku danych"""
        t = time.localtime(timestamp)
        hour = t[3]  # indeks 3 to godzina
        day = t[7]  # indeks 7 to dzień roku
        return f"{self.filename_prefix}{day}_{hour}.bin"

    def save_block(self, records, timestamp):
        """Zapisuje skompresowany blok danych"""
        try:
            compressed = self.compressor.compress_block(records)
            if compressed:
                filename = self.get_block_filename(timestamp)
                with open(filename, 'wb') as f:
                    f.write(compressed)
                return True
        except Exception as e:
            logger.error(f"Błąd zapisu bloku: {e}")
        return False

    def load_block(self, timestamp):
        """Wczytuje i dekompresuje blok danych"""
        try:
            filename = self.get_block_filename(timestamp)
            with open(filename, 'rb') as f:
                compressed = f.read()
            return self.compressor.decompress_block(compressed)
        except Exception as e:
            logger.error(f"Błąd odczytu bloku: {e}")
            return []

    def cleanup_old_blocks(self, max_days):
        """Usuwa stare bloki danych"""
        try:
            current_time = time.time()
            current_day = time.localtime(current_time)[7]  # indeks 7 to dzień roku

            for filename in os.listdir():
                if filename.startswith(self.filename_prefix):
                    try:
                        # Pobierz timestamp z nazwy pliku
                        day = int(filename.split('_')[1])
                        if (current_day - day) % 365 > max_days:
                            os.remove(filename)
                            logger.info(f"Usunięto stary blok: {filename}")
                    except:
                        continue
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia bloków: {e}")


# Singleton instance
block_manager = DataBlockManager()
