import asyncio
import json
import os
import logging
import aioble
import bluetooth
from led import led_controller, LEDController


logger = logging.getLogger("BluetoothService")

_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_WIFI_CREDENTIALS_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
_ADV_INTERVAL_MS = 250_000


class BluetoothService:
    """Handles BLE communication for receiving WiFi credentials."""

    def __init__(self, wifi_service):
        """
        Initializes the BluetoothService.

        Args:
            wifi_service: Service to check WiFi connection status.
        """
        self.wifi_service = wifi_service
        self.running = True

        self._ble_service = aioble.Service(_BLE_SERVICE_UUID)
        self._wifi_credentials_characteristic = aioble.Characteristic(
            self._ble_service,
            _BLE_WIFI_CREDENTIALS_UUID,
            read=True,
            write=True,
            notify=True,
            capture=True,
        )
        aioble.register_services(self._ble_service)

    async def start(self):
        """
        Starts BLE advertisement and listens for WiFi credentials.
        """
        logger.info("Uruchamianie Bluetooth Service, nasłuchiwanie danych BLE...")
        led_controller.set_state(LEDController.State.FLASHING)
        try:
            peripheral_task = asyncio.create_task(self._peripheral_task())
            credentials_task = asyncio.create_task(self._wait_for_wifi_credentials())

            await credentials_task
        except asyncio.CancelledError:
            logger.info("Bluetooth Service anulowany")
        finally:
            peripheral_task.cancel()
            try:
                await peripheral_task
            except asyncio.CancelledError:
                logger.info("Zadanie advertising BLE anulowane")
            logger.info("Bluetooth Service zatrzymany")

    async def _peripheral_task(self):
        """
        Advertises BLE service and waits for connections.
        """
        while self.running:
            try:
                async with await aioble.advertise(
                    _ADV_INTERVAL_MS, name="ESP32", services=[_BLE_SERVICE_UUID]
                ) as connection:
                    logger.info("Połączenie od %s", connection.device)
                    await connection.disconnected()
            except asyncio.CancelledError:
                logger.info("Zadanie peryferyjne BLE anulowane")
                break
            except Exception as e:
                logger.error("Błąd w zadaniu peryferyjnym BLE: %s", e)
            finally:
                await asyncio.sleep(0.1)

    async def _wait_for_wifi_credentials(self):
        """
        Waits for WiFi credentials via BLE and processes them.
        """
        START_BYTE = b'\x02'
        END_BYTE = b'\x03'
        buffer = b''
        transmission_started = False

        while self.running:
            try:
                connection, data = await self._wifi_credentials_characteristic.written()
                logger.info("Odebrano pakiet z danymi WiFi: %s", data)

                if data.startswith(START_BYTE):
                    transmission_started = True
                    logger.info("Rozpoczęto transmisję")
                    buffer = data[1:]
                elif data.endswith(END_BYTE):
                    buffer += data[:-1]
                    transmission_started = False
                    logger.info("Zakończono transmisję")
                    try:
                        credentials_str = buffer.decode('utf-8')
                        buffer = b''
                        credentials_dict = {}
                        for pair in credentials_str.split(','):
                            key, value = pair.split('=')
                            credentials_dict[key] = value
                        if (
                            'ssid' in credentials_dict
                            and 'password' in credentials_dict
                        ):
                            with open('wifi_credentials.json', 'w') as f:
                                json.dump(credentials_dict, f)
                            logger.info("Zapisano dane WiFi: %s", credentials_dict)
                            stored_connection = connection
                            max_retries = 10
                            for _ in range(max_retries):
                                if self.wifi_service.connected:
                                    try:
                                        if stored_connection:
                                            notification_data = b'OK'
                                            logger.info("Sending notification data: %s (hex: %s)", 
                                                      notification_data, 
                                                      notification_data.hex())
                                            self._wifi_credentials_characteristic.notify(
                                                stored_connection, notification_data
                                            )
                                            await asyncio.sleep(2)
                                    except Exception as e:
                                        logger.error("Błąd podczas wysyłania powiadomienia BLE: %s", e)
                                    finally:
                                        logger.info("Wyłączanie Bluetooth Service")
                                        self.running = False
                                        await aioble.stop()
                                        return
                                await asyncio.sleep(1)
                            logger.info("Nie udało się potwierdzić połączenia WiFi")
                        else:
                            logger.error("Nieprawidłowy format danych WiFi")
                    except ValueError:
                        logger.error("Błąd podczas dekodowania danych WiFi")
                elif transmission_started:
                    buffer += data
            except asyncio.CancelledError:
                logger.info("Zadanie oczekiwania na dane WiFi anulowane")
                break
            except Exception as e:
                logger.error("Błąd w zadaniu oczekiwania na dane WiFi: %s", e)
            finally:
                await asyncio.sleep(0.1)
