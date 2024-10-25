#include "WiFiManager.h"

void WiFiManager::connectSavedWiFi()
{
    WiFi.begin(); // Użyj zapisanych danych
    int attemptCounter = 0;
    while (WiFi.status() != WL_CONNECTED && attemptCounter < 10)
    {
        delay(1000);
        attemptCounter++;
        Serial.print(".");
    }
    Serial.println();
}

bool WiFiManager::connectToWiFi(const char *ssid, const char *password)
{
    WiFi.begin(ssid, password);
    int attemptCounter = 0;
    while (WiFi.status() != WL_CONNECTED && attemptCounter < 10)
    {
        delay(1000); // Może trwać dłużej, więc zapewnij WDT reset w innych miejscach
        Serial.print(".");
        attemptCounter++;
    }
    return WiFi.status() == WL_CONNECTED;
}

String WiFiManager::generateWiFiListHTML()
{
    int n = WiFi.scanNetworks();
    String html = "<html><body><h1>Dostępne sieci WiFi</h1><ul>";
    for (int i = 0; i < n; ++i)
    {
        html += "<li><a href='/connect?ssid=" + WiFi.SSID(i) + "'>" + WiFi.SSID(i) + "</a></li>";
    }
    html += "</ul></body></html>";
    return html;
}

