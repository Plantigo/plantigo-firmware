from machine import ADC, Pin
import time
import json
import uos as os


class SoilMoistureSensor:
    def __init__(self, pin_number=32):
        self.adc = ADC(Pin(pin_number))
        self.adc.atten(ADC.ATTN_11DB)  # Pełny zakres 0-3.3V
        self.CONFIG_FILE = "soil_calibration.json"

        # Domyślne wartości kalibracji
        self.calibration = {
            "dry": 3200,  # Wartość w powietrzu (sucho)
            "wet": 1800  # Wartość w wodzie (mokro)
        }

        # Sprawdź czy istnieje plik kalibracji
        if not self.load_calibration():
            print("\n*** Nie znaleziono kalibracji! ***")
            print("Rozpoczynam proces kalibracji...")
            self.start_calibration()

    def load_calibration(self):
        """Wczytuje zapisane wartości kalibracji z pliku. Zwraca True jeśli się udało."""
        try:
            if "soil_calibration.json" in os.listdir():
                with open(self.CONFIG_FILE, "r") as f:
                    self.calibration = json.loads(f.read())
                print(f"Załadowano kalibrację: sucho={self.calibration['dry']}, mokro={self.calibration['wet']}")
                return True
        except Exception as e:
            print(f"Używam domyślnej kalibracji: {e}")
        return False

    def save_calibration(self):
        """Zapisuje wartości kalibracji do pliku"""
        try:
            with open(self.CONFIG_FILE, "w") as f:
                f.write(json.dumps(self.calibration))
            print("Zapisano nową kalibrację")
        except Exception as e:
            print(f"Błąd zapisu kalibracji: {e}")

    def calibrate_dry(self):
        """Kalibracja dla suchej gleby/powietrza"""
        print("Kalibracja - SUCHO (czujnik w powietrzu)")
        value = self._average_reading(10)
        self.calibration["dry"] = value
        self.save_calibration()
        return value

    def calibrate_wet(self):
        """Kalibracja dla mokrej gleby/wody"""
        print("Kalibracja - MOKRO (czujnik w wodzie)")
        value = self._average_reading(10)
        self.calibration["wet"] = value
        self.save_calibration()
        return value

    def _average_reading(self, samples=5):
        """Zwraca średnią z pomiarów"""
        readings = []
        for _ in range(samples):
            readings.append(self.adc.read())
            time.sleep_ms(100)
        return sum(readings) // len(readings)

    def read(self):
        """Odczyt wilgotności gleby"""
        try:
            raw_value = self._average_reading()

            # Konwersja na procenty (0-100%)
            # Odwracamy wartości bo ADC daje większe wartości dla suchej gleby
            moisture = ((self.calibration["dry"] - raw_value) * 100) // (
                        self.calibration["dry"] - self.calibration["wet"])
            moisture = max(0, min(100, moisture))

            # print(f"Wilgotność gleby: {moisture}% (ADC: {raw_value})")
            return {
                "soil_moisture": moisture,
                "raw_value": raw_value
            }
        except Exception as e:
            # print(f"Błąd odczytu wilgotności gleby: {e}")
            return {
                "soil_moisture": None,
                "raw_value": None
            }

    def start_calibration(self):
        """Proces kalibracji czujnika"""
        print("\nKalibracja czujnika wilgotności gleby")
        print("1. Wyjmij czujnik z gleby i wytrzyj do sucha")
        print("2. Poczekaj 5 sekund...")
        time.sleep(5)
        dry = self.calibrate_dry()
        print(f"Wartość dla suchego czujnika: {dry}")

        print("\nTeraz zanurz czujnik w wodzie")
        print("Poczekaj 5 sekund...")
        time.sleep(5)
        wet = self.calibrate_wet()
        print(f"Wartość dla mokrego czujnika: {wet}")

        print("\nKalibracja zakończona!")
        print(f"Sucho (powietrze): {dry}")
        print(f"Mokro (woda): {wet}")


# Singleton instance
soil_sensor = SoilMoistureSensor(32)


def get_soil_moisture_data():
    """Funkcja pomocnicza do odczytu wilgotności gleby"""
    return soil_sensor.read()


def calibrate():
    """Funkcja pomocnicza do wymuszenia kalibracji"""
    soil_sensor.start_calibration()


