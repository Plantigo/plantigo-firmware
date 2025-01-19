import network
import time
import ujson
import asyncio
from led import led_controller, LEDController


async def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Czekaj na połączenie
    timeout = 10  # Czas oczekiwania na połączenie
    start_time = time.time()
    while not wlan.isconnected() and time.time() - start_time < timeout:
        await asyncio.sleep(1)

    if wlan.isconnected():
        print("Connected to Wi-Fi")
        print("IP address:", wlan.ifconfig()[0])
        while True:
            if not wlan.isconnected():
                print("Wi-Fi connection lost. Reconnecting...")
                wlan.connect(ssid, password)

            led_controller.set_state(LEDController.State.ENABLED)
            await asyncio.sleep(5)
    else:
        print("Failed to connect to Wi-Fi")


# Funkcja do zapisania danych SSID i hasła w pamięci flash
def save_wifi_credentials(ssid, password):
    credentials = {"ssid": ssid, "password": password}
    with open('wifi_config.json', 'w') as f:
        ujson.dump(credentials, f)
        print("Wi-Fi credentials saved.")


# Funkcja do odczytania danych z pamięci flash
def load_wifi_credentials():
    try:
        with open('wifi_credentials.json', 'r') as f:
            credentials = ujson.load(f)
            return credentials.get('ssid'), credentials.get('password')
    except OSError:
        print("No Wi-Fi credentials found.")
        return None, None
