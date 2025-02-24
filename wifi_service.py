import asyncio
import json
import logging
from led import LEDController, led_controller
import network
import time
from utils import file_exists

logger = logging.getLogger("WiFiService")


class WiFiService:
    """Handles WiFi connection and monitors credential file."""

    def __init__(self):
        self.connected = False

    async def connect(self) -> bool:
        """Attempts to connect to WiFi using stored credentials."""
        if not file_exists("wifi_credentials.json"):
            return False

        with open("wifi_credentials.json", "r") as file:
            credentials = json.load(file)

        ssid, password = credentials.get("ssid"), credentials.get("password")

        if not ssid or not password:
            logger.info("Niepoprawne dane logowania do WiFi")
            return False

        return await self._attempt_connect(ssid, password)

    async def _attempt_connect(self, ssid: str, password: str) -> bool:
        """
        Handles the connection attempt to WiFi with provided credentials.

        This method encapsulates the logic required to establish a WiFi connection.
        """
        logger.info(f"Łączenie z WiFi: {ssid}...")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(ssid, password)

        timeout = 10
        start_time = time.time()
        while not self.wlan.isconnected() and (time.time() - start_time < timeout):
            await asyncio.sleep(1)

        if self.wlan.isconnected():
            self.connected = True
            logger.info("LED enabled")
            led_controller.set_state(LEDController.State.ENABLED)
            logger.info("Połączono z WiFi!")
            logger.info("📡 IP address: %s", self.wlan.ifconfig()[0])
            return True
        else:
            logger.info("❌ Failed to connect to WiFi")
            return False

    async def watch_for_credentials(self):
        """Checks every 5s if credentials file is created."""
        while not self.connected:
            if file_exists("wifi_credentials.json"):
                logger.info(
                    "Plik wifi_credentials.json wykryty, próbuję połączyć się..."
                )
                if await self.connect():
                    return
            await asyncio.sleep(5)
