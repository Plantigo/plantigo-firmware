#ifndef USER_MANAGER_H
#define USER_MANAGER_H

#include <WiFi.h>
extern String header; // Deklaracja zmiennej globalnej

void handleClientConnection();
bool isUserRecognized(String ip, int &index);
void addUser(String ip);
void incrementConnectionCount(int index);

#endif