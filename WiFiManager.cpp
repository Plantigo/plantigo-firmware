#include <Arduino.h>
#include <WiFi.h>

char ssid[30];
const char *password = "123456789";

void initializeWiFi()
{
    WiFi.softAP("Temp_SSID", password);
    String macAddress = WiFi.softAPmacAddress();
    macAddress.replace(":", "_");                           
    sprintf(ssid, "ESP32_HOTSPOT_%s", macAddress.c_str()); 

    WiFi.softAP(ssid, password); // Ustaw SSID i hasło
    IPAddress IP = WiFi.softAPIP();
    Serial.print("Setting AP SSID: ");
    Serial.println(ssid);
    Serial.print("AP IP address: ");
    Serial.println(IP);
    Serial.print("ESP32 MAC Address: ");
    Serial.println(macAddress); // Wyświetl adres MAC
}