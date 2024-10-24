#include <Arduino.h>
#include <WebSocketsServer.h>
#include "WebSocketHandler.h"

WebSocketsServer webSocket = WebSocketsServer(81);
unsigned long lastRandomSend = 0; // Dodaj definicję zmiennej tutaj

void webSocketEvent(uint8_t num, WStype_t type, uint8_t *payload, size_t length)
{
    if (type == WStype_CONNECTED)
    {
        Serial.println("Client connected to WebSocket.");
    }
    else if (type == WStype_DISCONNECTED)
    {
        Serial.println("Client disconnected from WebSocket.");
    }
}

void initializeWebSocket()
{
    webSocket.begin();
    webSocket.onEvent(webSocketEvent);
}

void handleWebSocket()
{
    webSocket.loop();
}

void sendRandomValues()
{
    unsigned long currentMillis = millis();
    if (currentMillis - lastRandomSend > random(1000, 3000))
    {
        int value1 = random(0, 101);
        int value2 = random(0, 101);
        int value3 = random(0, 101);
        String randomValues = String(value1) + "," + String(value2) + "," + String(value3);
        webSocket.broadcastTXT(randomValues);
        lastRandomSend = currentMillis;
    }
}