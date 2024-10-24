#include <Arduino.h>
#include "Heartbeat.h"

unsigned long startTimestamp;
unsigned long lastHeartbeat = 0; // Dodana zmienna, która przechowuje czas ostatniego wywołania

void initializeHeartbeat()
{
    startTimestamp = millis();
}

void logHeartbeat()
{
    unsigned long currentTimestamp = millis();

    // Loguj heartbeat co 10 sekund
    if (currentTimestamp - lastHeartbeat >= 10000)
    {
        Serial.print("Heartbeat - ESP Running: ");
        Serial.print((currentTimestamp - startTimestamp) / 1000);
        Serial.print(" seconds, Current Timestamp: ");
        Serial.println(currentTimestamp);

        lastHeartbeat = currentTimestamp; // Aktualizuj czas ostatniego wywołania
    }
}