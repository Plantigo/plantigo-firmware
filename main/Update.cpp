#include "Update.h"

OTAUpdater::OTAUpdater(AsyncWebServer& server) {
    server.on(
        "/update", HTTP_POST,
        [](AsyncWebServerRequest *request) {
            bool hasError = Update.hasError();
            request->send(200, "text/plain", hasError ? "FAIL" : "OK");
            if (!hasError) {
                ESP.restart();
            }
        },
        [this](AsyncWebServerRequest *request, const String& filename, size_t index, uint8_t *data, size_t len, bool final) {
            handleOTAUpdate(request, filename, index, data, len, final);
        }
    );
}

void OTAUpdater::begin() {
    Serial.println("OTA Updater initialized");
}

void OTAUpdater::handleOTAUpdate(AsyncWebServerRequest *request, const String& filename, size_t index, uint8_t *data, size_t len, bool final) {
    if (index == 0) {
        Serial.printf("Rozpoczynanie aktualizacji: %s\n", filename.c_str());
        if (!Update.begin(UPDATE_SIZE_UNKNOWN)) {
            Update.printError(Serial);
        }
    }
    if (Update.write(data, len) != len) {
        Update.printError(Serial);
    }
    if (final) {
        if (Update.end(true)) {
            Serial.println("Aktualizacja zakończona sukcesem.");
        } else {
            Update.printError(Serial);
        }
    }
}