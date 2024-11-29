#ifndef UPDATE_H
#define UPDATE_H

#include <ESPAsyncWebServer.h>
#include <Update.h>

class OTAUpdater {
public:
    OTAUpdater(AsyncWebServer& server);
    void begin();

private:
    void handleOTAUpdate(AsyncWebServerRequest *request, const String& filename, size_t index, uint8_t *data, size_t len, bool final);
};

#endif // UPDATE_H