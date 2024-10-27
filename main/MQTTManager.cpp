#include "MQTTManager.h"
#include <Preferences.h>

Preferences preferences;

MQTTManager::MQTTManager(PubSubClient &client) : mqttClient(client), connected(false)
{
}

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

bool MQTTManager::connect(const String &mac)
{
    Serial.print("Connecting to MQTT server at ");
    Serial.print(mqttHost);
    Serial.print(":");
    Serial.println(mqttPort);

    if (mqttClient.connect(mac.c_str(), mqttUser.c_str(), mqttPassword.c_str()))
    {
        connected = true;
        Serial.println("MQTT Connected!");
        return true;
    }
    else
    {
        connected = false;
        Serial.print("MQTT Connection failed, state: ");
        Serial.println(mqttClient.state()); // Wyświetla kod błędu
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

void MQTTManager::loadSettings()
{
    preferences.begin("mqtt", true);
    mqttHost = preferences.getString("host", "");
    mqttPort = preferences.getInt("port", 1883);
    mqttUser = preferences.getString("user", "");
    mqttPassword = preferences.getString("password", "");
    preferences.end();

    if (!mqttHost.isEmpty() && mqttPort > 0)
    {
        mqttClient.setServer(mqttHost.c_str(), mqttPort);
    }
}

void MQTTManager::saveSettings()
{
    preferences.begin("mqtt", false);
    preferences.putString("host", mqttHost);
    preferences.putInt("port", mqttPort);
    preferences.putString("user", mqttUser);
    preferences.putString("password", mqttPassword);
    preferences.end();
}