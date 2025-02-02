import bluetooth_service
from wifi_service import load_wifi_credentials, connect_wifi
import asyncio
from led import led_controller, LEDController
from mqtt_service import MQTTService

def log(message):
    print(f"[LOG] {message}")

async def boot():
    log("Booting...")
    
    bluetooth_task_started = False
    mqtt_service = MQTTService()
    
    asyncio.create_task(led_controller.start())

    while True:
        ssid, password = load_wifi_credentials()
        log(f"SSID: {ssid}, Password: {password}")
        
        if ssid and password:
            wifi_connected = await connect_wifi(ssid, password)
            
            if wifi_connected:
                log("Połączono z Wi-Fi, próbuję połączyć się z MQTT...")

                while True:
                    if mqtt_service.connect():
                        log("✅ Połączono z MQTT!")
                        mqtt_service.subscribe()
                        asyncio.create_task(mqtt_service.listen())
                        asyncio.create_task(mqtt_service.publish_data())
                        break
                    else:
                        log("❌ Błąd połączenia z MQTT. Ponowna próba za 5s...")
                        await asyncio.sleep(5)
                
                while True:
                    await asyncio.sleep(5) 
            else:
                log("❌ Nie udało się połączyć z Wi-Fi. Ponowna próba za 5s...")
        else:
            if not bluetooth_task_started:
                asyncio.create_task(bluetooth_service.start())
                bluetooth_task_started = True
            log("Brak zapisanych danych WiFi, sprawdzanie ponownie za 5 sekund...")
        await asyncio.sleep(5)  

asyncio.run(boot())
