#ifndef SENSORMANAGER_H
#define SENSORMANAGER_H

#include <PubSubClient.h>

class SensorManager
{
public:
    SensorManager(PubSubClient &client);
    void startSendingData();
    void loop();

private:
    PubSubClient &mqttClient;
    String macAddress;
    void generateAndSendData();
    unsigned long lastSendTime;
};

#endif