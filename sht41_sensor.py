from machine import I2C, Pin
import time

# Adres I2C dla SHT41
SHT41_I2C_ADDR = 0x44


class SHT41Sensor:
    def __init__(self, scl_pin=22, sda_pin=21):
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000)

    def read(self):
        """Odczyt temperatury i wilgotności z SHT41"""
        try:
            # Wysłanie komendy pomiaru (high precision)
            self.i2c.writeto(SHT41_I2C_ADDR, bytes([0xFD]))
            time.sleep_ms(10)

            # Odczyt 6 bajtów danych
            data = self.i2c.readfrom(SHT41_I2C_ADDR, 6)

            # Konwersja danych temperatury
            temp_raw = (data[0] << 8) | data[1]
            temperature = -45 + 175 * temp_raw / 65535

            # Konwersja danych wilgotności
            hum_raw = (data[3] << 8) | data[4]
            humidity = -6 + 125 * hum_raw / 65535

            temperature = round(temperature, 1)
            humidity = round(humidity, 1)

            print(f"SHT41 - Temperatura: {temperature:.1f}°C, Wilgotność: {humidity:.1f}%")
            return {
                "temperature": temperature,
                "humidity": humidity
            }
        except Exception as e:
            return {
                "temperature": None,
                "humidity": None
            }


# Singleton instance
sht41_sensor = SHT41Sensor()


def get_sht41_data():
    """Funkcja pomocnicza do odczytu danych z SHT41"""
    return sht41_sensor.read()
