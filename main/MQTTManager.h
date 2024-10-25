#ifndef MQTTMANAGER_H
#define MQTTMANAGER_H

#include <PubSubClient.h>

class MQTTManager
{
public:
    MQTTManager(PubSubClient &client);
    void setMQTTServer(const String &host, int port);
    void setCredentials(const String &user, const String &password);
    bool connect();
    bool isConnected();
    void loop();
    String getHost();
    int getPort();

private:
    PubSubClient &mqttClient;
    String mqttHost;
    int mqttPort;
    String mqttUser;
    String mqttPassword;
    bool connected;
};

#endif