#include <Arduino.h>
#include <WiFi.h>
#include "UserManager.h"

struct User
{
    String ip;
    int connectionCount;
};

User userList[255];
int userCount = 0;

bool isUserRecognized(String ip, int &index)
{
    for (int i = 0; i < userCount; i++)
    {
        if (userList[i].ip == ip)
        {
            index = i;
            return true;
        }
    }
    return false;
}

void addUser(String ip)
{
    if (userCount < 255)
    {
        userList[userCount].ip = ip;
        userList[userCount].connectionCount = 1;
        userCount++;
    }
}

void incrementConnectionCount(int index)
{
    userList[index].connectionCount++;
}

extern WiFiServer server; // Odwołanie do globalnego serwera

void handleClientConnection()
{
    WiFiClient client = server.available(); // Użyj globalnego serwera
    if (client)
    {
        Serial.println("New client connected");
        String currentLine = "";
        String clientIP = client.remoteIP().toString();
        String espMac = WiFi.softAPmacAddress();
        int userIndex;
        bool recognized = isUserRecognized(clientIP, userIndex);

        if (recognized)
        {
            incrementConnectionCount(userIndex);
        }
        else
        {
            addUser(clientIP);
            userIndex = userCount - 1;
        }

        while (client.connected())
        {
            if (client.available())
            {
                char c = client.read();
                header += c; // Korzystanie z globalnej zmiennej header
                if (c == '\n')
                {
                    if (currentLine.length() == 0)
                    {
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:text/html");
                        client.println("Connection: close");
                        client.println();

                        client.println("<!DOCTYPE html><html>");
                        client.println("<head><meta http-equiv='content-type' content='text/html; charset=utf-8' /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
                        client.println("<style>");
                        client.println("body { font-family: Arial, sans-serif; background-color: #f0f0f0; color: #333; text-align: center; padding: 50px; }");
                        client.println(".container { background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }");
                        client.println("h1 { font-size: 36px; color: #4CAF50; }");
                        client.println("p { font-size: 18px; color: #555; }");
                        client.println("</style></head>");
                        client.println("<body><div class='container'>");

                        client.println("<p>ESP32 MAC Address: " + espMac + "</p>");

                        if (recognized)
                        {
                            client.println("<h1>Witaj</h1>");
                            client.println("<p>IP Address: " + clientIP + "</p>");
                            client.println("<p>Connection Count: " + String(userList[userIndex].connectionCount) + "</p>");
                        }
                        else
                        {
                            client.println("<h1>Cześć</h1>");
                            client.println("<p>IP Address: " + clientIP + "</p>");
                            client.println("<p>This is your first connection.</p>");
                        }

                        client.println("<p id='randomValues'>Waiting for data...</p>");
                        client.println("<p id='currentTime'></p>");
                        client.println("<script>");
                        client.println("let ws = new WebSocket('ws://' + window.location.hostname + ':81/');");
                        client.println("ws.onmessage = function(event) {");
                        client.println("  document.getElementById('randomValues').innerText = 'Random Values: ' + event.data;");
                        client.println("};");
                        client.println("function updateCurrentTime() {");
                        client.println("  setInterval(() => {");
                        client.println("    const now = new Date();");
                        client.println("    const formattedTime = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');");
                        client.println("    document.getElementById('currentTime').innerText = 'Current Time: ' + formattedTime;");
                        client.println("  }, 1000);");
                        client.println("}");
                        client.println("updateCurrentTime();");
                        client.println("</script>");
                        client.println("</div></body></html>");
                        client.println();
                        break;
                    }
                    else
                    {
                        currentLine = "";
                    }
                }
                else if (c != '\r')
                {
                    currentLine += c;
                }
            }
        }
        header = "";
        client.stop();
        Serial.println("Client disconnected");
    }
}