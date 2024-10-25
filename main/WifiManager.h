#ifndef WiFiManager_h
#define WiFiManager_h

#include <WiFi.h>

class WiFiManager
{
public:
    void connectSavedWiFi();
    bool connectToWiFi(const char *ssid, const char *password);
    String generateWiFiListHTML();
};

#endif