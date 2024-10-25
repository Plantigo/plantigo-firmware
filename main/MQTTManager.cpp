#include "MQTTManager.h"

MQTTManager::MQTTManager(PubSubClient &client) : mqttClient(client), connected(false) {}

void MQTTManager::setMQTTServer(const String &host, int port)
{
    mqttHost = host;
    mqttPort = port;
    mqttClient.setServer(mqttHost.c_str(), mqttPort);
}

void MQTTManager::setCredentials(const String &user, const String &password)
{
    mqttUser = user;
    mqttPassword = password;
}

bool MQTTManager::connect()
{
    if (mqttClient.connect("ESP32Client", mqttUser.c_str(), mqttPassword.c_str()))
    {
        connected = true;
        Serial.println("MQTT Connected!");
        return true;
    }
    else
    {
        connected = false;
        Serial.println("MQTT Connection failed.");
        return false;
    }
}

bool MQTTManager::isConnected()
{
    return mqttClient.connected();
}

void MQTTManager::loop()
{
    if (mqttClient.connected())
    {
        mqttClient.loop();
    }
}

String MQTTManager::getHost()
{
    return mqttHost;
}

int MQTTManager::getPort()
{
    return mqttPort;
}