#include <Arduino.h>
#include <WiFi.h>
#include "WiFiManager.h"
#include "WebSocketHandler.h"
#include "UserManager.h"
#include "Heartbeat.h"

String header;         // Globalna zmienna na nagłówki
WiFiServer server(80); // Globalna zmienna serwera na porcie 80

void setup()
{
    Serial.begin(115200);
    initializeWiFi();      // Funkcja konfigurująca WiFi
    server.begin();        // Uruchomienie serwera na porcie 80
    Serial.println("Server started on port 80");
    initializeWebSocket(); // Inicjalizacja WebSocketów
    initializeHeartbeat(); // Inicjalizacja Heartbeat
}

void loop()
{
    handleWebSocket();        // Obsługa połączeń WebSocket
    logHeartbeat();           // Logowanie heartbeat co kilka sekund
    sendRandomValues();       // Przesyłanie losowych wartości przez WebSocket
    handleClientConnection(); // Obsługa klientów HTTP
}