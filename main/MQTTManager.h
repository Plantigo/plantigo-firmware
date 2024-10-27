#ifndef MQTTMANAGER_H
#define MQTTMANAGER_H

#include <PubSubClient.h>
#include <Preferences.h>

class MQTTManager
{
public:
    MQTTManager(PubSubClient &client);
    void setMQTTServer(const String &host, int port);
    void setCredentials(const String &user, const String &password);
    bool connect(const String &mac);
    bool isConnected();
    void loop();
    String getHost();
    int getPort();
    void saveSettings();
    void loadSettings();

private:
    PubSubClient &mqttClient;
    String mqttHost;
    int mqttPort;
    String mqttUser;
    String mqttPassword;
    bool connected;

   
};

#endif