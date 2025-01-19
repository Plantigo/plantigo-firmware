import bluetooth_service
from wifi_service import load_wifi_credentials, connect_wifi
import asyncio
from led import led_controller, LEDController


async def boot():
    print("Booting...")

    bluetooth_task_started = False
    asyncio.create_task(led_controller.start())

    while True:
        ssid, password = load_wifi_credentials()
        print(f"SSID: {ssid}, Password: {password}")
        if ssid and password:
            await connect_wifi(ssid, password)
            break
        else:
            if not bluetooth_task_started:
                asyncio.create_task(bluetooth_service.start())
                bluetooth_task_started = True
            await asyncio.sleep(5)  # Check again after 5 seconds


asyncio.run(boot())
