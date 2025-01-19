# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/micropython-esp32-bluetooth-low-energy-ble/

from micropython import const
import asyncio
import aioble
import bluetooth
import json
from led import led_controller, LEDController
from wifi_service import connect_wifi


# See the following for generating UUIDs:
# https://www.uuidgenerator.net/
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_WIFI_CREDENTIALS_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

# Register GATT server, the service and characteristics
ble_service = aioble.Service(_BLE_SERVICE_UUID)
wifi_credentials_characteristic = aioble.Characteristic(
    ble_service,
    _BLE_WIFI_CREDENTIALS_UUID,
    read=True,
    write=True,
    notify=True,
    capture=True,
)

# Register service(s)
aioble.register_services(ble_service)


# Serially wait for connections. Don't advertise while a central is connected.
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="ESP32",
                services=[_BLE_SERVICE_UUID],
            ) as connection:
                print("Connection from", connection.device)
                await connection.disconnected()
        except asyncio.CancelledError:
            # Catch the CancelledError
            print("Peripheral task cancelled")
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            # Ensure the loop continues to the next iteration
            await asyncio.sleep_ms(100)


START_BYTE = b'\x02'
END_BYTE = b'\x03'


async def wait_for_wifi_credentials():
    buffer = b''
    transmission_started = False
    while True:
        try:
            connection, data = await wifi_credentials_characteristic.written()
            print('Received WiFi credentials packet:', data)

            if data.startswith(START_BYTE):
                transmission_started = True
                print('Transmission started')
                buffer = data[1:]  # Remove the start byte
            elif data.endswith(END_BYTE):
                buffer += data[:-1]  # Remove the end byte
                transmission_started = False
                print('Transmission ended')
                # Decode the complete data
                credentials = buffer.decode('utf-8')
                buffer = b''  # Reset buffer for next transmission
                try:
                    credentials_dict = {}
                    for pair in credentials.split(','):
                        key, value = pair.split('=')
                        credentials_dict[key] = value
                    if 'ssid' in credentials_dict and 'password' in credentials_dict:
                        with open('wifi_credentials.json', 'w') as f:
                            json.dump(credentials_dict, f)
                        print('WiFi credentials saved:', credentials_dict)
                        print('Disabling Bluetooth')
                        await aioble.stop()  # Disable Bluetooth
                        return
                    else:
                        print('Invalid WiFi credentials format')
                except ValueError:
                    print('Error decoding WiFi credentials')
            elif transmission_started:
                buffer += data
        except asyncio.CancelledError:
            # Catch the CancelledError
            print("WiFi credentials task cancelled")
        except Exception as e:
            print("Error in wait_for_wifi_credentials:", e)
        finally:
            # Ensure the loop continues to the next iteration
            await asyncio.sleep_ms(100)


# Run tasks
async def start():
    print("Starting BLE loop...")
    t1 = asyncio.create_task(peripheral_task())
    t2 = asyncio.create_task(wait_for_wifi_credentials())
    led_controller.set_state(LEDController.State.FLASHING)
    await asyncio.gather(t1, t2)
