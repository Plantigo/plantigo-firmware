from machine import Pin
import uasyncio as asyncio
import os
import machine
import logging
from config_manager import config


logger = logging.getLogger("ButtonController")


class ButtonController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ButtonController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            gpio_pin = config.get('button', 'gpio_pin')
            self.button = Pin(gpio_pin, Pin.IN, Pin.PULL_UP)
            self.press_start = None
            self.initialized = True
            self.LONG_PRESS_DURATION = config.get('button', 'long_press_duration')
            self.DEBOUNCE_MS = config.get('button', 'debounce_ms') / 1000.0  # konwersja na sekundy

    async def start(self):
        """
        Monitoruje stan przycisku i wykonuje reset po długim przyciśnięciu
        """
        while True:
            if self.button.value() == 0:  # Przycisk wciśnięty (stan niski ze względu na PULL_UP)
                if self.press_start is None:
                    self.press_start = asyncio.get_event_loop().time()
                    logger.info("Przycisk wciśnięty")
                else:
                    current_time = asyncio.get_event_loop().time()
                    if current_time - self.press_start >= self.LONG_PRESS_DURATION:
                        logger.info("Wykryto długie przyciśnięcie - resetowanie urządzenia...")
                        # Usuń plik z danymi WiFi
                        try:
                            os.remove("wifi_credentials.json")
                            logger.info("Usunięto plik wifi_credentials.json")
                        except:
                            logger.info("Nie znaleziono pliku wifi_credentials.json")
                        
                        # Zaczekaj chwilę przed resetem
                        await asyncio.sleep(1)
                        # Reset urządzenia
                        machine.reset()
            else:
                if self.press_start is not None:
                    self.press_start = None
            
            await asyncio.sleep(self.DEBOUNCE_MS)  # Używamy skonfigurowanego czasu debounce


# Singleton instance
button_controller = ButtonController() y