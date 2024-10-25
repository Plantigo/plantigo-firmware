#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <PubSubClient.h>
#include "WiFiManager.h"
#include "esp_task_wdt.h"

// Ustawienia WiFi, MQTT i serwera
WiFiClient espClient;
PubSubClient mqttClient(espClient);
AsyncWebServer server(80);
WiFiManager wifiManager;
String selectedSSID = "";
bool mqttConnected = false;

// Placeholdery do MQTT
String mqttHost = "";
int mqttPort = 1883;
String mqttUser = "";
String mqttPassword = "";

// Zawartość HTML przechowywana bezpośrednio w pamięci
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>WiFi & MQTT Manager</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; }
        .container { width: 80%; margin: auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1, h2 { text-align: center; }
        .form { display: flex; flex-direction: column; align-items: center; }
        input, select { margin: 10px 0; padding: 10px; width: 80%; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .hidden { display: none; }
        .info { margin-top: 20px; padding: 10px; background-color: #e9f7e9; border: 1px solid #b2e8b2; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>WiFi & MQTT Manager</h1>
        <div id="wifi-section">
            <h2>Wybierz sieć WiFi</h2>
            <select id="ssid-select"></select>
            <input type="password" id="wifi-password" placeholder="Wpisz hasło">
            <button onclick="connectWiFi()">Połącz</button>
        </div>

        <div id="mqtt-section" class="hidden">
            <h2>Ustawienia MQTT</h2>
            <input type="text" id="mqtt-host" placeholder="MQTT Host">
            <input type="text" id="mqtt-port" placeholder="MQTT Port">
            <input type="text" id="mqtt-user" placeholder="MQTT User">
            <input type="password" id="mqtt-password" placeholder="MQTT Password">
            <button onclick="connectMQTT()">Zapisz</button>
            <p id="mqtt-status"></p>
        </div>

        <div id="connection-info" class="hidden info">
            <h2>Informacje o połączeniu</h2>
            <p id="wifi-info"></p>
            <p id="mqtt-info"></p>
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", () => {
            checkConnectionStatus();
        });

        function checkConnectionStatus() {
            fetch('/status').then(response => response.json()).then(data => {
                if (data.wifiConnected) {
                    document.getElementById("wifi-section").classList.add("hidden");
                    document.getElementById("mqtt-section").classList.remove("hidden");
                    showConnectionInfo(data);
                } else {
                    document.getElementById("wifi-section").classList.remove("hidden");
                    document.getElementById("mqtt-section").classList.add("hidden");
                    fetchAvailableNetworks();
                }
            });
        }

        function showConnectionInfo(data) {
            const wifiInfo = document.getElementById("wifi-info");
            const mqttInfo = document.getElementById("mqtt-info");

            if (data.wifiConnected) {
                wifiInfo.innerHTML = `SSID: ${data.ssid}<br>IP: ${data.ip}<br>RSSI: ${data.rssi}`;
                document.getElementById("connection-info").classList.remove("hidden");
            }

            if (data.mqttConnected) {
                mqttInfo.innerHTML = `MQTT Host: ${data.mqttHost}<br>Port: ${data.mqttPort}<br>Status: CONNECTED`;
            } else {
                mqttInfo.innerHTML = "MQTT Status: NOT CONNECTED";
            }
        }

        function fetchAvailableNetworks() {
            fetch('/scan').then(response => response.json()).then(data => {
                const ssidSelect = document.getElementById("ssid-select");
                data.networks.forEach(ssid => {
                    const option = document.createElement("option");
                    option.value = ssid;
                    option.textContent = ssid;
                    ssidSelect.appendChild(option);
                });
            });
        }

        function connectWiFi() {
            const ssid = document.getElementById("ssid-select").value;
            const password = document.getElementById("wifi-password").value;
            fetch('/connect', {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `ssid=${encodeURIComponent(ssid)}&password=${encodeURIComponent(password)}`
            }).then(response => response.text()).then(result => {
                if (result === "connected") {
                    alert("Połączono z siecią WiFi");
                    location.reload();
                } else {
                    alert("Nie udało się połączyć z siecią WiFi.");
                }
            });
        }

        function connectMQTT() {
            const host = document.getElementById("mqtt-host").value;
            const port = document.getElementById("mqtt-port").value;
            const user = document.getElementById("mqtt-user").value;
            const password = document.getElementById("mqtt-password").value;
            fetch('/mqtt', {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: `mqtt_host=${host}&mqtt_port=${port}&mqtt_user=${user}&mqtt_password=${password}`
            }).then(response => response.text()).then(result => {
                const statusEl = document.getElementById("mqtt-status");
                if (result === "connected") {
                    statusEl.textContent = "CONNECTED";
                    statusEl.style.color = "green";
                    checkConnectionStatus();
                } else {
                    statusEl.textContent = "NOT CONNECTED";
                    statusEl.style.color = "red";
                }
            });
        }
    </script>
</body>
</html>
)rawliteral";

void setup()
{
    Serial.begin(115200);
    esp_task_wdt_init(60, true);
    esp_task_wdt_delete(xTaskGetIdleTaskHandleForCPU(0));
    esp_task_wdt_delete(xTaskGetIdleTaskHandleForCPU(1));
    wifiManager.connectSavedWiFi();
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("Brak zapisanych danych WiFi lub nie udało się połączyć. Tworzenie hotspotu...");
        WiFi.softAP("ESP32-AP");
    }
    else
    {
        Serial.println("Połączono z zapisanym WiFi.");
        Serial.print("Adres IP: ");
        Serial.println(WiFi.localIP());
    }

    // Obsługa serwowania strony głównej
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request)
              {
        IPAddress clientIP = request->client()->remoteIP();
        Serial.print("Nowe połączenie od: ");
        Serial.println(clientIP.toString());
        request->send_P(200, "text/html", index_html); });

    // Endpoint do skanowania sieci WiFi
    server.on("/scan", HTTP_GET, [](AsyncWebServerRequest *request)
              {
        int n = WiFi.scanNetworks();
        String json = "{\"networks\":[";
        for (int i = 0; i < n; ++i) {
            if (i > 0) json += ",";
            json += "\"" + WiFi.SSID(i) + "\"";
        }
        json += "]}";
        request->send(200, "application/json", json); });

    // Endpoint do sprawdzania statusu połączenia WiFi i MQTT
    server.on("/status", HTTP_GET, [](AsyncWebServerRequest *request)
              {
        bool wifiConnected = (WiFi.status() == WL_CONNECTED);
        bool mqttStatus = mqttConnected;
        String ssid = wifiConnected ? WiFi.SSID() : "";
        String ip = wifiConnected ? WiFi.localIP().toString() : "";
        int rssi = wifiConnected ? WiFi.RSSI() : 0;
        
        String json = "{\"wifiConnected\":" + String(wifiConnected ? "true" : "false") +
                      ",\"mqttConnected\":" + String(mqttStatus ? "true" : "false") +
                      ",\"ssid\":\"" + ssid +
                      "\",\"ip\":\"" + ip +
                      "\",\"rssi\":" + String(rssi) +
                      ",\"mqttHost\":\"" + mqttHost +
                      "\",\"mqttPort\":" + String(mqttPort) + "}";
        request->send(200, "application/json", json); });

    server.on("/connect", HTTP_POST, [](AsyncWebServerRequest *request)
              {
        if (request->hasParam("ssid", true) && request->hasParam("password", true)) {
            selectedSSID = request->getParam("ssid", true)->value();
            String password = request->getParam("password", true)->value();
            if (wifiManager.connectToWiFi(selectedSSID.c_str(), password.c_str())) {
                request->send(200, "text/plain", "connected");
                ESP.restart();
            } else {
                request->send(200, "text/plain", "failed");
            }
        } });

    server.on("/mqtt", HTTP_POST, [](AsyncWebServerRequest *request)
              {
        if (request->hasParam("mqtt_host", true) && request->hasParam("mqtt_port", true)) {
            mqttHost = request->getParam("mqtt_host", true)->value();
            mqttPort = request->getParam("mqtt_port", true)->value().toInt();
            mqttUser = request->getParam("mqtt_user", true)->value();
            mqttPassword = request->getParam("mqtt_password", true)->value();
            mqttClient.setServer(mqttHost.c_str(), mqttPort);
            connectToMQTT();
            request->send(200, "text/plain", mqttConnected ? "connected" : "failed");
        } });

    server.begin();
}

void loop()
{
    if (mqttClient.connected())
    {
        mqttClient.loop();
    }
    esp_task_wdt_reset();
}

void connectToMQTT()
{
    if (mqttClient.connect("ESP32Client", mqttUser.c_str(), mqttPassword.c_str()))
    {
        mqttConnected = true;
        Serial.println("MQTT Connected!");
    }
    else
    {
        mqttConnected = false;
        Serial.println("MQTT Connection failed.");
    }
}