#include "SensorManager.h"
#include <Arduino.h>
#include <WiFi.h>

SensorManager::SensorManager(PubSubClient &client) : mqttClient(client), lastSendTime(0)
{
    macAddress = WiFi.macAddress();
    macAddress.replace(":", "-");
}

void SensorManager::startSendingData()
{
    Serial.println("Starting to send simulated sensor data...");
}

void SensorManager::loop()
{
    unsigned long currentMillis = millis();
    if (currentMillis - lastSendTime > random(2000, 5000))
    { 
        generateAndSendData();
        lastSendTime = currentMillis;
    }
}

void SensorManager::generateAndSendData()
{
    int sensor1 = random(0, 101);
    int sensor2 = random(0, 101);
    int sensor3 = random(0, 101);
    int sensor4 = random(0, 101);

    String payload = "{\"sensor1\":" + String(sensor1) +
                     ",\"sensor2\":" + String(sensor2) +
                     ",\"sensor3\":" + String(sensor3) +
                     ",\"sensor4\":" + String(sensor4) + "}";

    String topic = "sensors/" + macAddress + "/data";

    if (mqttClient.connected())
    {
        mqttClient.publish(topic.c_str(), payload.c_str());
        Serial.print("Wysłano dane na temat ");
        Serial.print(topic);
        Serial.print(": ");
        Serial.println(payload);
    }
}