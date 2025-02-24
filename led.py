from machine import Pin
import uasyncio as asyncio
import logging


logger = logging.getLogger("LEDController")


class LEDController:
    _instance = None

    class State:
        DISABLED = 0
        FLASHING = 1
        ENABLED = 2

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LEDController, cls).__new__(cls)
        return cls._instance

    def __init__(self, pin_number):
        if not hasattr(self, 'initialized'):
            self.led = Pin(pin_number, Pin.OUT)
            self.state = self.State.DISABLED
            self.initialized = True

    def set_state(self, state):
        self.state = state
        if state == self.State.DISABLED:
            logger.info("LED disabled.")
            self.led.value(0)
        elif state == self.State.ENABLED:
            self.led.value(1)
        else:
            logger.info("LED flashing.")

    async def start(self):
        while True:
            if self.state == self.State.FLASHING:
                self.led.value(1)
                await asyncio.sleep(1)
                self.led.value(0)
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(1)


led_controller = LEDController(2)
