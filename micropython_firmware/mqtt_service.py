import json
import asyncio
import network
import ubinascii
import random
import os
import machine
from umqtt.simple import MQTTClient
from temperature_sensor import get_temperature
from humidity_sensor import get_humidity
from pressure_sensor import get_pressure
from light_sensor import get_light

def load_mqtt_credentials():
    """Ładuje dane MQTT z pliku JSON."""
    try:
        with open("mqtt_credentials.json", "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Błąd wczytywania pliku MQTT: {e}")
        return None

def save_mqtt_credentials(data):
    """Zapisuje nowe dane MQTT do pliku JSON."""
    try:
        with open("mqtt_credentials.json", "w") as file:
            json.dump(data, file)
        print("Dane MQTT zaktualizowane.")
    except Exception as e:
        print(f"Błąd zapisu MQTT: {e}")

def save_wifi_credentials(ssid, password):
    """Zapisuje nowe dane WiFi do pliku JSON."""
    try:
        with open("wifi_credentials.json", "w") as file:
            json.dump({"ssid": ssid, "password": password}, file)
        print("Dane WiFi zaktualizowane.")
    except Exception as e:
        print(f"Błąd zapisu WiFi: {e}")

def delete_file(filename):
    """Usuwa plik, jeśli istnieje."""
    try:
        if filename in os.listdir():
            os.remove(filename)
            print(f"Plik {filename} usunięty.")
        else:
            print(f"Plik {filename} nie istnieje.")
    except Exception as e:
        print(f"Błąd usuwania {filename}: {e}")

class MQTTService:
    def __init__(self):
        self.client = None
        self.credentials = load_mqtt_credentials()
        self.mac_address = self.get_mac_address()
        self.data_topic = f"{self.credentials['data_topic_prefix']}{self.mac_address}/{self.credentials['data_topic_suffix']}" if self.credentials else None

    def get_mac_address(self):
        """Pobiera adres MAC ESP32."""
        wlan = network.WLAN(network.STA_IF)
        mac = ubinascii.hexlify(wlan.config('mac'), ':').decode()
        return mac.replace(':', '')  # Usuwamy dwukropki dla czytelności

    def connect(self):
        """Łączy się z brokerem MQTT."""
        if not self.credentials:
            print("Brak danych do MQTT.")
            return False

        self.client = MQTTClient(
            client_id="ESP32_Client",
            server=self.credentials["broker"],
            port=self.credentials["port"],
            user=self.credentials["username"],
            password=self.credentials["password"]
        )

        try:
            self.client.connect()
            print("Połączono z MQTT")
            return True
        except Exception as e:
            print(f"Błąd połączenia z MQTT: {e}")
            return False

    def subscribe(self):
        """Subskrybuje temat 'command'."""
        if not self.client or not self.credentials:
            print("Nie można subskrybować - brak połączenia.")
            return

        topic = self.credentials["command_topic"]
        self.client.set_callback(self.on_message)
        self.client.subscribe(topic)
        print(f"Subskrybowano temat: {topic}")

    def on_message(self, topic, msg):
        """Obsługuje wiadomości z MQTT."""
        try:
            data = json.loads(msg.decode())
            code = data.get("code")

            if code == 1:  # Zmiana danych MQTT
                payload = data.get("payload", {})
                new_mqtt_name = payload.get("mqtt_name")
                new_mqtt_password = payload.get("mqtt_password")

                if new_mqtt_name and new_mqtt_password:
                    self.credentials["username"] = new_mqtt_name
                    self.credentials["password"] = new_mqtt_password
                    save_mqtt_credentials(self.credentials)
                    print("Zmieniono dane MQTT. Restart wymagany!")

            elif code == 2:  # Restart ESP32
                print("Restartowanie urządzenia...")
                machine.reset()

            elif code == 3:  # Zmiana danych WiFi
                payload = data.get("payload", {})
                new_ssid = payload.get("wifi_ssid")
                new_password = payload.get("wifi_password")

                if new_ssid and new_password:
                    save_wifi_credentials(new_ssid, new_password)
                    print("Zmieniono dane WiFi. Restart wymagany!")

            elif code == 4:  # Usunięcie wifi_credentials.json
                delete_file("wifi_credentials.json")

            elif code == 5:  # Usunięcie mqtt_credentials.json
                delete_file("mqtt_credentials.json")

            else:
                print(f"Otrzymano nieznany kod: {code}")

        except Exception as e:
            print(f"Błąd parsowania wiadomości MQTT: {e}")

    async def publish_data(self):
        """Publikuje losowe liczby w formacie JSON dla sensorów na '<prefix>/<mac_address>/<sufix>', co 5 sekund."""
        while True:
            if self.client and self.data_topic:
                sensor_data = {
                    "temperature": get_temperature(),
                    "humidity": get_humidity(),
                    "pressure": get_pressure(),
                    "light": get_light()
                }
                payload = json.dumps(sensor_data)
                
                try:
                    self.client.publish(self.data_topic, payload)
                    print(f"Wysłano na {self.data_topic}: {payload}")
                except Exception as e:
                    print(f"Błąd publikowania MQTT: {e}")

            await asyncio.sleep(5)

    async def listen(self):
        """Nasłuchuje wiadomości w pętli."""
        while True:
            try:
                self.client.check_msg()
            except Exception as e:
                print(f"Błąd nasłuchiwania MQTT: {e}")
            await asyncio.sleep(1)  # Sprawdza co 1 sekundę
