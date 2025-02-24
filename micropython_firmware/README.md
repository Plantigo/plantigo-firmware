# PlantIGo Firmware

Firmware dla systemu monitorowania roślin oparty na ESP32 i MicroPython.

## Funkcjonalności

- Odczyt danych z czujników:
  - Temperatura i wilgotność powietrza (SHT41)
  - Wilgotność powietrza (DHT22 jako backup)
  - Wilgotność gleby (Capacitive Soil Moisture Sensor v2.0)
  - Natężenie światła (BH1750)
- Komunikacja:
  - Serwer HTTP z API REST
  - Komunikacja MQTT
  - Konfiguracja przez Bluetooth (BLE)
- Przechowywanie danych:
  - Efektywny format binarny
  - Automatyczna rotacja danych
  - Konfigurowalny okres przechowywania
- Fizyczny przycisk reset
- Konfigurowalność przez plik JSON

## Wymagania systemowe

### Sprzęt
- ESP32 (minimum 4MB flash)
- Czujniki:
  - SHT41 lub DHT22 (temperatura i wilgotność)
  - Capacitive Soil Moisture Sensor v2.0
  - BH1750 (natężenie światła)
- Przycisk reset (opcjonalnie)
- Zasilanie 3.3V

### Oprogramowanie
- MicroPython v1.19 lub nowszy
- esptool.py do wgrywania firmware
- mpremote lub ampy do zarządzania plikami

## Instalacja

1. Wgranie MicroPython:
```bash
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20220117-v1.19.1.bin
```

2. Wgranie plików projektu:
```bash
mpremote cp config.json :config.json
mpremote cp *.py :
```

3. Pierwsze uruchomienie:
```bash
mpremote repl
>>> import main
```

## Podłączenie czujników

### SHT41 (I2C)
```
ESP32           SHT41
3.3V  -------- VDD
GND   -------- GND
GPIO21 ------- SDA
GPIO22 ------- SCL
```

### DHT22 (backup)
```
ESP32           DHT22
3.3V  -------- VDD (pin 1)
GPIO23 ------- DATA (pin 2)
-      ------- PIN3 (niepodłączony)
GND   -------- GND (pin 4)
```
Wymagany rezystor podciągający 10kΩ między VDD a DATA.
Pin 3 DHT22 nie jest używany w tym czujniku, więc pozostaje niepodłączony.

### Capacitive Soil Moisture Sensor v2.0
```
ESP32           Soil Sensor
3.3V  -------- VCC
GND   -------- GND
GPIO32 ------- AOUT
```

### BH1750 (I2C)
```
ESP32           BH1750
3.3V  -------- VCC
GND   -------- GND
GPIO21 ------- SDA (współdzielony z SHT41)
GPIO22 ------- SCL (współdzielony z SHT41)
```
Uwaga: BH1750 używa tej samej magistrali I2C co SHT41, ale ma inny adres (0x23 lub 0x5C).

### Przycisk Reset
```
ESP32           Button
GPIO0  -------- PIN1
GND    -------- PIN2
```

## Konfiguracja (config.json)

### Sekcja data_storage
```json
"data_storage": {
    "sensor_data_filename": "sensor_data.bin",  // Nazwa pliku z danymi
    "max_days_to_keep": 7                       // Okres przechowywania danych (dni)
}
```

### Sekcja sampling
```json
"sampling": {
    "mqtt_publish_interval": 5,    // Interwał publikowania MQTT (sekundy)
    "sensor_read_interval": 5      // Interwał odczytu czujników (sekundy)
}
```

### Sekcja web_server
```json
"web_server": {
    "port": 80,                    // Port serwera HTTP
    "debug": true                  // Tryb debug
}
```

### Sekcja sensors
```json
"sensors": {
    "temperature_precision": 2,     // Precyzja temperatury (miejsca po przecinku)
    "humidity_precision": 2,        // Precyzja wilgotności
    "soil_moisture_precision": 1    // Precyzja wilgotności gleby
}
```

### Sekcja button
```json
"button": {
    "gpio_pin": 0,                 // Pin GPIO przycisku
    "long_press_duration": 5,      // Czas długiego przyciśnięcia (sekundy)
    "debounce_ms": 50             // Czas debounce (milisekundy)
}
```

## API HTTP

### GET /api/sensors
Pobiera aktualne odczyty z czujników.

Przykładowa odpowiedź:
```json
{
    "temperature": 23.45,      // °C, 2 miejsca po przecinku
    "humidity": 45.67,        // %, 2 miejsca po przecinku
    "soil_moisture": 78.9,    // %, 1 miejsce po przecinku
    "light": 850,            // lx, liczba całkowita
    "timestamp": 1709892345  // Unix timestamp
}
```

### GET /api/sensors/history
Pobiera historyczne dane z określonego okresu.

Parametry:
- `hours` - liczba godzin wstecz (domyślnie 24)

Przykład: `/api/sensors/history?hours=48`

Przykładowa odpowiedź:
```json
[
    {
        "temperature": 23.45,
        "humidity": 45.67,
        "soil_moisture": 78.9,
        "light": 850,
        "timestamp": 1709892345
    },
    {
        "temperature": 23.48,
        "humidity": 45.89,
        "soil_moisture": 79.1,
        "light": 855,
        "timestamp": 1709892350
    }
]
```

### GET /api/config
Pobiera aktualną konfigurację.

Przykładowa odpowiedź:
```json
{
    "data_storage": {
        "sensor_data_filename": "sensor_data.bin",
        "max_days_to_keep": 7,
        "compression": true,
        "sampling_rate": {
            "day_start_hour": 6,
            "day_end_hour": 22,
            "day_interval": 5,
            "night_interval": 30
        }
    },
    "sampling": {
        "mqtt_publish_interval": 5,
        "sensor_read_interval": 5
    },
    "sensors": {
        "temperature_precision": 2,
        "humidity_precision": 2,
        "soil_moisture_precision": 1,
        "light_precision": 0
    }
}
```

### POST /api/config
Aktualizuje konfigurację.

Przykład zmiany interwałów próbkowania:
```bash
curl -X POST http://<ip_esp32>/api/config \
     -H "Content-Type: application/json" \
     -d '{
           "data_storage": {
             "sampling_rate": {
               "day_interval": 10,
               "night_interval": 60
             }
           }
         }'
```

### GET /api/system
Pobiera informacje o stanie systemu.

Przykładowa odpowiedź:
```json
{
    "memory": {
        "flash_total_kb": 4096,       // Całkowita pamięć flash w KB
        "flash_free_kb": 3200,        // Wolna pamięć flash w KB
        "flash_used_percent": 21.9,   // Procent wykorzystanej pamięci flash
        "ram_free_kb": 48,           // Wolna pamięć RAM w KB
        "ram_used_kb": 16,           // Wykorzystana pamięć RAM w KB
        "ram_used_percent": 25.0     // Procent wykorzystanej pamięci RAM
    },
    "storage": {
        "block_count": 168,          // Liczba zapisanych bloków danych
        "current_block_size": 45,    // Rozmiar aktualnego bufora
        "max_block_size": 100        // Maksymalny rozmiar bloku
    },
    "sampling": {
        "current_interval": 5,       // Aktualny interwał próbkowania (sekundy)
        "is_day_mode": true,         // Czy aktywny tryb dzienny
        "next_mode_change_hour": 22  // Godzina następnej zmiany trybu
    }
}
```

## Format danych i optymalizacja

### Format rekordu
Dane są przechowywane w formacie binarnym dla efektywności:
- Timestamp: 8 bajtów (double)
- Temperatura: 4 bajty (float)
- Wilgotność: 4 bajty (float)
- Wilgotność gleby: 4 bajty (float)
- Natężenie światła: 4 bajty (float)
Łącznie: 24 bajty na rekord

### System kompresji
- Dane grupowane w bloki po 100 rekordów
- Kompresja DEFLATE (uzlib)
- Współczynnik kompresji: 2-5x
- Automatyczna kompresja przy zapisie
- Transparentna dekompresja przy odczycie

### Inteligentne próbkowanie
```json
"sampling_rate": {
    "day_start_hour": 6,      // Początek trybu dziennego
    "day_end_hour": 22,       // Koniec trybu dziennego
    "day_interval": 5,        // Interwał dzienny (sekundy)
    "night_interval": 30      // Interwał nocny (sekundy)
}
```
- Tryb dzienny (6:00-22:00): próbkowanie co 5 sekund
- Tryb nocny (22:00-6:00): próbkowanie co 30 sekund
- Automatyczne przełączanie trybów
- Oszczędność miejsca ~4x w nocy

### Organizacja danych
- Dane zapisywane w blokach godzinowych
- Każdy blok to osobny plik
- Format nazwy: `data_block_<dzień>_<godzina>.bin`
- Automatyczna rotacja starych danych
- Konfigurowalny okres przechowywania (domyślnie 7 dni)

### Zużycie pamięci
Przykładowe obliczenia dla 7 dni:
1. Tryb dzienny (16h):
   - 16h × 3600s ÷ 5s = 11520 rekordów
   - 11520 × 24B = 276,480 bajtów
2. Tryb nocny (8h):
   - 8h × 3600s ÷ 30s = 960 rekordów
   - 960 × 24B = 23,040 bajtów
3. Łącznie na dzień:
   - 299,520 bajtów
   - Po kompresji ~100KB
4. 7 dni:
   - ~700KB po kompresji

### Optymalizacje
1. Buforowanie:
   - Aktualny blok trzymany w RAM
   - Zapis na flash tylko pełnych bloków
   - Minimalizacja operacji I/O

2. Precyzja danych:
```json
"sensors": {
    "temperature_precision": 2,     // °C, 2 miejsca po przecinku
    "humidity_precision": 2,        // %, 2 miejsca po przecinku
    "soil_moisture_precision": 1,   // %, 1 miejsce po przecinku
    "light_precision": 0           // lx, liczby całkowite
}
```

## Funkcje bezpieczeństwa

1. Przycisk reset:
   - Długie przyciśnięcie (domyślnie 5s) usuwa dane WiFi i resetuje urządzenie
   - Pozwala na rekonfigurację w przypadku problemów

2. Backup czujników:
   - DHT22 jako zapasowy czujnik wilgotności
   - Automatyczne przełączanie w przypadku awarii SHT41

## Pierwsze uruchomienie

1. Wgraj firmware na ESP32
2. Przy pierwszym uruchomieniu urządzenie wejdzie w tryb konfiguracji BLE
3. Połącz się przez aplikację mobilną i skonfiguruj WiFi
4. Po połączeniu z WiFi urządzenie automatycznie uruchomi serwer HTTP i MQTT

## Rozwiązywanie problemów

1. Reset do ustawień fabrycznych:
   - Przytrzymaj przycisk przez 5 sekund
   - Urządzenie usunie dane WiFi i się zrestartuje

2. Problemy z czujnikami:
   - Sprawdź logi przez MQTT lub serwer HTTP
   - Wartości NULL w odczytach wskazują na problem z czujnikiem

3. Problemy z pamięcią:
   - Sprawdź wolne miejsce: `import os; os.statvfs('/')`
   - Zmniejsz interwały próbkowania w config.json
   - Skróć okres przechowywania danych (max_days_to_keep)
   - Włącz kompresję jeśli wyłączona
   - Usuń niepotrzebne pliki z flash

4. Optymalizacja zużycia pamięci:
   - Dostosuj interwały do potrzeb:
     ```json
     "sampling_rate": {
         "day_interval": 30,    // Rzadsze próbkowanie w dzień
         "night_interval": 120  // Bardzo rzadkie w nocy
     }
     ```
   - Zmniejsz precyzję danych:
     ```json
     "sensors": {
         "temperature_precision": 1,  // Mniej miejsc po przecinku
         "humidity_precision": 1,
         "soil_moisture_precision": 0,
         "light_precision": 0
     }
     ```
   - Włącz agresywną kompresję:
     ```json
     "data_storage": {
         "compression": true,
         "block_size": 200      // Większe bloki = lepsza kompresja
     }
     ```

5. Problemy z wydajnością:
   - Zwiększ interwały próbkowania
   - Zmniejsz rozmiar bloków kompresji
   - Wyłącz debug w web_server
   - Zredukuj częstotliwość publikacji MQTT

6. Monitorowanie systemu:
   - Endpoint `/api/system` zwraca informacje o:
     - Wolnej pamięci
     - Liczbie zapisanych bloków
     - Współczynniku kompresji
     - Aktualnym interwale próbkowania 

## Komunikacja MQTT

### Tematy MQTT

1. Dane czujników:
```
plantigo/<device_id>/sensors           # Aktualne odczyty
plantigo/<device_id>/sensors/history   # Historia odczytów
```

2. Status systemu:
```
plantigo/<device_id>/status           # Status urządzenia (online/offline)
plantigo/<device_id>/system           # Informacje systemowe
plantigo/<device_id>/errors           # Błędy i ostrzeżenia
```

3. Konfiguracja:
```
plantigo/<device_id>/config           # Aktualna konfiguracja
plantigo/<device_id>/config/update    # Aktualizacja konfiguracji
```

### Format wiadomości MQTT

1. Dane czujników (sensors):
```json
{
    "temperature": 23.45,
    "humidity": 45.67,
    "soil_moisture": 78.9,
    "light": 850,
    "timestamp": 1709892345
}
```

2. Status systemu (system):
```json
{
    "uptime": 3600,           // Czas pracy w sekundach
    "wifi_strength": -65,     // Siła sygnału WiFi w dBm
    "free_memory": 32768,     // Wolna pamięć w bajtach
    "battery": 3.9           // Napięcie baterii (jeśli dostępne)
}
```

## Konfiguracja BLE

### Charakterystyki BLE

1. Konfiguracja WiFi:
```
UUID: 0xFFF1 - Zapis SSID
UUID: 0xFFF2 - Zapis hasła WiFi
UUID: 0xFFF3 - Status połączenia
```

2. Konfiguracja systemu:
```
UUID: 0xFFF4 - Odczyt/zapis konfiguracji JSON
UUID: 0xFFF5 - Status konfiguracji
```

### Proces parowania BLE

1. Urządzenie w trybie parowania:
   - Nazwa: "PlantIGo-XXXX" (XXXX = ostatnie 4 znaki MAC)
   - Service UUID: 0xFFF0
   
2. Sekwencja konfiguracji:
   - Połącz z urządzeniem
   - Zapisz SSID (0xFFF1)
   - Zapisz hasło (0xFFF2)
   - Sprawdź status (0xFFF3)
   - Opcjonalnie: skonfiguruj system (0xFFF4)

## Aktualizacja firmware

1. Przez HTTP:
```bash
curl -X POST http://<ip_esp32>/api/update \
     -F "firmware=@firmware.bin"
```

2. Przez MQTT:
```
plantigo/<device_id>/update/firmware  # Topic do aktualizacji
plantigo/<device_id>/update/status    # Status aktualizacji
```

## Bezpieczeństwo

1. Szyfrowanie danych:
   - HTTPS dla API (opcjonalnie)
   - MQTT z TLS
   - Szyfrowane hasła WiFi w pamięci

2. Uwierzytelnianie:
   - Token API dla HTTP
   - Certyfikaty dla MQTT
   - PIN dla BLE

3. Zabezpieczenia fizyczne:
   - Przycisk reset (5s)
   - Watchdog timer
   - Backup konfiguracji

## Rozwiązywanie problemów

// ... existing code ...

7. Problemy z MQTT:
   - Sprawdź konfigurację brokera
   - Zweryfikuj certyfikaty TLS
   - Sprawdź logi połączenia
   - Upewnij się, że QoS jest odpowiedni

8. Problemy z BLE:
   - Upewnij się, że urządzenie jest w trybie parowania
   - Sprawdź zasięg (max 10m)
   - Zresetuj moduł BLE
   - Usuń sparowane urządzenia

9. Problemy z aktualizacją:
   - Sprawdź sumę kontrolną firmware
   - Upewnij się, że masz wystarczająco miejsca
   - Wykonaj kopię zapasową konfiguracji
   - W razie problemów użyj trybu recovery

10. Diagnostyka przez API:
    ```bash
    # Sprawdź status systemu
    curl http://<ip_esp32>/api/system
    
    # Pobierz logi
    curl http://<ip_esp32>/api/logs
    
    # Test czujników
    curl http://<ip_esp32>/api/sensors/test
    ```

## Licencja

MIT License - szczegóły w pliku LICENSE
