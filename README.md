# Dokumentacja MQTT dla ESP32

## 1. Opis systemu
ESP32 łączy się z brokerem MQTT i komunikuje się za pomocą tematów (topics). Odbiera komendy na temat `command_topic` oraz publikuje dane z sensorów na `data_topic`.

## 2. Struktura wiadomości

### 2.1 Wiadomości wysyłane do ESP32 (`command_topic`)

ESP32 nasłuchuje na temat `command_topic` i interpretuje otrzymane wiadomości w formacie JSON.

#### Przykładowa struktura wiadomości:
```json
{
  "code": <numer_kodu>,
  "payload": {
    <dodatkowe_dane>
  }
}
```

### 2.2 Obsługiwane kody komend

| Kod | Opis | Przykładowa wiadomość |
|------|------|----------------------|
| `1`  | Zmiana danych MQTT (login/hasło) | ```json { "code": 1, "payload": { "mqtt_name": "nowy_user", "mqtt_password": "nowe_haslo" } } ``` |
| `2`  | Restart ESP32 | ```json { "code": 2 } ``` |
| `3`  | Zmiana danych WiFi | ```json { "code": 3, "payload": { "wifi_ssid": "NowaSiec", "wifi_password": "NoweHaslo" } } ``` |
| `4`  | Usunięcie pliku `wifi_credentials.json` | ```json { "code": 4 } ``` |
| `5`  | Usunięcie pliku `mqtt_credentials.json` | ```json { "code": 5 } ``` |

---

## 3. Wiadomości publikowane przez ESP32 (`data_topic`)

ESP32 co 5 sekund publikuje dane z sensorów na `data_topic`, który ma format:
```
<data_topic_prefix>/<mac_address>/<data_topic_suffix>
```

### Przykładowa struktura wiadomości:

```json
{
  "temperature": 22.5,
  "humidity": 55.0,
  "pressure": 1013.25,
  "light": 120
}
```

Dane są pobierane z odpowiednich sensorów i automatycznie publikowane na brokerze MQTT.

---

## 4. Konfiguracja

Dane konfiguracyjne MQTT i WiFi są przechowywane w plikach:
- `mqtt_credentials.json`
- `wifi_credentials.json`

Przykładowa zawartość `mqtt_credentials.json`:
```json
{
  "broker": "mqtt.example.com",
  "port": 1883,
  "username": "esp32",
  "password": "securepassword",
  "command_topic": "command",
  "data_topic_prefix": "sensors/",
  "data_topic_suffix": "/data"
}
```

Przykładowa zawartość `wifi_credentials.json`:
```json
{
  "ssid": "MojaSiec",
  "password": "BezpieczneHaslo"
}
```

---

## 5. Jak zmienić ustawienia?

### 5.1 Zmiana danych WiFi
1. Wysłać wiadomość MQTT z kodem `3`, podając nowy `ssid` i `password`.
2. Urządzenie automatycznie zapisze nowe dane i wymaga restartu.

### 5.2 Zmiana danych MQTT
1. Wysłać wiadomość MQTT z kodem `1`, podając nowy `mqtt_name` i `mqtt_password`.
2. Urządzenie zapisze zmiany i wymaga restartu.

### 5.3 Ręczne usunięcie plików
Można wysłać komendy `4` lub `5`, aby usunąć odpowiednio `wifi_credentials.json` lub `mqtt_credentials.json`.

---

## 6. Restart ESP32
Można zrestartować urządzenie poprzez:
- Wysłanie wiadomości MQTT z kodem `2`.
- Ręczne odłączenie i podłączenie zasilania.

---

## 7. Debugowanie

Jeśli wystąpią problemy z połączeniem MQTT, ESP32 może wyświetlać komunikaty błędów w konsoli:
- **"Błąd połączenia z MQTT"** – sprawdzić ustawienia brokera i dane logowania.
- **"Brak danych do MQTT"** – plik `mqtt_credentials.json` nie istnieje lub jest niepoprawny.
- **"Błąd publikowania MQTT"** – broker może być niedostępny lub ESP32 nie ma połączenia z siecią.

W przypadku problemów zaleca się wysłać komendę `4` lub `5`, aby usunąć ustawienia i ponownie skonfigurować urządzenie.

---
