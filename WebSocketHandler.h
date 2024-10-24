#ifndef WEBSOCKET_HANDLER_H
#define WEBSOCKET_HANDLER_H

#include <WebSocketsServer.h> // Dodaj ten nagłówek, aby uzyskać dostęp do typów i klas WebSockets

extern unsigned long lastRandomSend; // Użyj extern, aby zadeklarować zmienną globalną

void initializeWebSocket();
void handleWebSocket();
void sendRandomValues();

#endif