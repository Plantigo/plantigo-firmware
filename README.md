# ESP32 Menedżer WiFi & MQTT

Projekt ten dostarcza prosty interfejs do zarządzania połączeniami WiFi oraz konfiguracją MQTT na ESP32. Użytkownicy mogą łączyć się z dostępnych sieci WiFi, ustawiać konfigurację MQTT oraz wysyłać symulowane dane z czujników do brokera MQTT.

## Funkcje

- **Zarządzanie WiFi:** Skanuj i łącz się z dostępnymi sieciami WiFi za pomocą interfejsu webowego.
- **Konfiguracja MQTT:** Ustawienia brokera MQTT (host, port, nazwa użytkownika i hasło).
- **Symulowane dane z czujników:** Po połączeniu z brokerem MQTT ESP32 wysyła losowe dane z czujników do skonfigurowanego tematu MQTT.
- **Interfejs Webowy:** Dostarcza przyjazny użytkownikowi interfejs do zarządzania ustawieniami WiFi i MQTT bezpośrednio z przeglądarki.
- **Automatyczne przełączanie Hotspotu:** Jeśli nie znaleziono zapisanych sieci WiFi, ESP32 tworzy hotspot, aby użytkownik mógł skonfigurować ustawienia WiFi.

## Wymagania sprzętowe

- Płytka deweloperska ESP32

## Wymagane biblioteki

Upewnij się, że masz zainstalowane następujące biblioteki w Arduino IDE:

1. **ESP Async Web Server**:
    - [ESPAsyncWebServer](https://github.com/me-no-dev/ESPAsyncWebServer)
2. **Async TCP**:
    - [AsyncTCP](https://github.com/me-no-dev/AsyncTCP)
3. **PubSubClient**:
    - [PubSubClient](https://github.com/knolleary/pubsubclient)
4. **ESP32 WiFi Library**:
    - Wbudowana w środowisko ESP32

## Instrukcja instalacji

1. Skonfiguruj Arduino IDE do pracy z ESP32 zgodnie z instrukcjami z [oficjalnej dokumentacji](https://github.com/espressif/arduino-esp32).
2. Pobierz i zainstaluj wymagane biblioteki, korzystając z powyższych linków.
3. Sklonuj ten projekt lub skopiuj kod do nowego szkicu w Arduino IDE.
4. Wgraj szkic na swoją płytkę ESP32.

## Jak to działa?

1. **Uruchomienie i Połączenie z WiFi**:
   - Po uruchomieniu ESP32 próbuje połączyć się z zapisanymi danymi WiFi.
   - Jeśli połączenie się nie powiedzie, ESP32 tworzy hotspot (np. `ESP32-AP`), aby umożliwić użytkownikowi połączenie i konfigurację WiFi.
   - Po połączeniu z hotspotem, otwórz przeglądarkę i przejdź do `192.168.4.1`, aby uzyskać dostęp do interfejsu webowego.

2. **Interfejs Webowy**:
   - **Sekcja WiFi**: Umożliwia wybór sieci WiFi, wpisanie hasła i połączenie.
   - **Sekcja MQTT**: Po nawiązaniu połączenia z WiFi pojawia się sekcja ustawień MQTT. Wprowadź ustawienia brokera i zapisz.
   - **Informacje o połączeniu**: Sekcja informacyjna wyświetla aktualny stan połączenia z WiFi i MQTT.

3. **Symulowane Dane z Czujników**:
   - Po nawiązaniu połączenia z brokerem MQTT, ESP32 zaczyna wysyłać losowe dane z czujników w losowych odstępach czasu.
   - Dane są wysyłane na temat MQTT w formacie `sensors/mac_address/data`.

## Struktura kodu

### `main.ino`

Kod główny zarządza połączeniem WiFi, hotspotem i serwerem webowym, oraz inicjalizuje moduły MQTT i Sensor.

### `WiFiManager.h` i `WiFiManager.cpp`

Odpowiada za zarządzanie połączeniami WiFi oraz tworzeniem hotspotu.

### `MQTTManager.h` i `MQTTManager.cpp`

Odpowiada za konfigurację i połączenie z brokerem MQTT.

### `SensorManager.h` i `SensorManager.cpp`

Generuje symulowane dane z czujników i wysyła je do brokera MQTT.

## Przykładowe zastosowanie

1. Włącz ESP32.
2. Połącz się z `ESP32-AP` i przejdź do `192.168.4.1`.
3. Wybierz sieć WiFi, wpisz hasło i połącz.
4. Po uzyskaniu połączenia z WiFi skonfiguruj ustawienia MQTT.
5. Ciesz się automatycznym wysyłaniem danych z czujników przez MQTT!

## Wskazówki

- **Reset połączenia WiFi**: Jeśli chcesz zresetować zapisane połączenia WiFi, wgraj ponownie kod na ESP32.
- **Problemy z połączeniem**: Upewnij się, że ustawienia WiFi i MQTT są poprawne i broker MQTT działa poprawnie.

