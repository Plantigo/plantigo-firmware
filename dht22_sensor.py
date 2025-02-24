from machine import Pin
import dht
import time


class DHT22Sensor:
    def __init__(self, pin_number=23):
        self.sensor = dht.DHT22(Pin(pin_number))

    def read(self):
        """Odczyt temperatury i wilgotności z DHT22"""
        try:
            self.sensor.measure()
            temperature = self.sensor.temperature()
            humidity = self.sensor.humidity()
            # print(f"DHT22 - Temperatura: {temperature:.1f}°C, Wilgotność: {humidity:.1f}%")
            return {
                "temperature": temperature,
                "humidity": humidity
            }
        except Exception as e:
            print(f"Błąd odczytu DHT22: {e}")
            return {
                "temperature": None,
                "humidity": None
            }


# Singleton instance
dht22_sensor = DHT22Sensor(23)  # Pin 23


def get_dht22_data():
    """Funkcja pomocnicza do odczytu danych z DHT22"""
    return dht22_sensor.read()
