import asyncio
from utils import file_exists
from wifi_service import WiFiService
from bluetooth_service import BluetoothService
from mqtt_service import MQTTService
import logging
from led import LEDController, led_controller


logging.basicConfig(level=logging.INFO, format="[%(name)s] %(message)s")
logger = logging.getLogger(__name__)


async def main():
    """
    Main boot function to initialize services and monitor WiFi credentials.
    """
    wifi_service = WiFiService()
    bluetooth_service = BluetoothService(wifi_service)
    mqtt_service = MQTTService()

    tasks = []
    tasks.append(asyncio.create_task(led_controller.start()))

    async def maintain_led_state():
        while True:
            if wifi_service.connected:
                led_controller.set_state(LEDController.State.ENABLED)
            await asyncio.sleep(5)

    tasks.append(asyncio.create_task(maintain_led_state()))

    if file_exists("wifi_credentials.json"):
        logger.info(
            "Plik wifi_credentials.json istnieje, próbuję połączyć się z WiFi..."
        )
        connected = await wifi_service.connect()
        if connected:
            logger.info("Połączono z WiFi, uruchamiam MQTT Service...")
            tasks.append(asyncio.create_task(mqtt_service.start()))
        else:
            logger.info(
                "Nie udało się połączyć z WiFi, uruchamiam Bluetooth Service oraz watch_for_credentials..."
            )
            tasks.append(asyncio.create_task(bluetooth_service.start()))
            tasks.append(asyncio.create_task(wifi_service.watch_for_credentials()))
    else:
        logger.info(
            "Brak pliku wifi_credentials.json, uruchamiam Bluetooth Service oraz watch_for_credentials..."
        )
        tasks.append(asyncio.create_task(bluetooth_service.start()))
        tasks.append(asyncio.create_task(wifi_service.watch_for_credentials()))

    mqtt_started = False
    while not mqtt_started:
        if file_exists("wifi_credentials.json") and wifi_service.connected:
            logger.info(
                "Wykryto plik wifi_credentials.json oraz połączenie WiFi, uruchamiam MQTT Service..."
            )
            tasks.append(asyncio.create_task(mqtt_service.start()))
            mqtt_started = True
        await asyncio.sleep(1)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

