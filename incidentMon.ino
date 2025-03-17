
/*
 File    : incidentMon.ino - Light up LEDs from via MQTT
 Author  : Joe McManus josephmc@alumni.cmu.edu
 Version : 0.1 2025/03/15
 Copyright (C) 2025 Joe McManus

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public Licensex
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#include <WiFi.h>
#include <Wire.h>
#include <PubSubClient.h>
#include "Qwiic_LED_Stick.h"

// WiFi network name and password:
const char* networkName = "ssid";
const char* networkPswd = "pass";

const char* ID = "esp32c3";
const char* ledOne = "ledOne";
LED LEDStickOne;
/*
   Red 255, 0 0
   Green 0, 255, 0
   Blue 0, 0, 255
   Yellow 255,255,0
   https://www.rapidtables.com/web/color/RGB_Color.html
*/

IPAddress broker(192, 168, 1, 2);

WiFiClient wclient;
PubSubClient client(wclient);  // Setup MQTT client

// Handle incomming messages from the broker
void callback(char* topic, byte* payload, unsigned int length) {
  String response;
  // Add somethign here
  //for (int i = 0; i < length; i++) {
  //  response += (char)payload[i];
  //}
  if (strcmp(topic, "ledOne") == 0) {
    Serial.print("Topic : ");
    Serial.println(topic);
    for (int i = 0; i < length; i++) {
      response += (char)payload[i];
    }
    setLED(LEDStickOne, response.toInt());
  }
}

void setup_wifi() {
  Serial.print("\nConnecting to ");
  Serial.println(networkName);

  WiFi.begin(networkName, networkPswd);  // Connect to network

  while (WiFi.status() != WL_CONNECTED) {  // Wait for connection
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  // blink blue 2x when wifi connects

  setLED(LEDStickOne, 1);

  setLED(LEDStickOne, 0);
}
// Reconnect to client
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(ID)) {
      client.subscribe(ledOne);
      Serial.println("connected");
      //blink 2 times when connected to Mqtt
      setLED(LEDStickOne, 5);
      setLED(LEDStickOne, 0);
    } else {
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setLED(LED& LEDStick, int level) {
  Serial.println(level);
  LEDStick.setLEDBrightness(0);
  for (int i = 1; i <= 10; i++) {
    if (level == 0) {
      LEDStick.setLEDColor(i, 0, 0, 0);
    } else if (level == 1) {
      LEDStick.setLEDColor(i, 0, 0, 255);
    } else if (level == 2) {
      LEDStick.setLEDColor(i, 0, 255, 0);
    } else if (level == 3) {
      LEDStick.setLEDColor(i, 255, 255, 0);
    } else if (level == 4) {
      LEDStick.setLEDColor(i, 255, 0, 0);
    } else if (level == 5) {
      //Set all to white, maybe use for debugging?
      LEDStick.setLEDColor(i, 255, 255, 255);
    }
  }
  // Pulse in and out 5 times
  for (int i = 1; i <= 5; i++) {
    for (int j = 1; j <= 10; j++) {
      LEDStick.setLEDBrightness(j);
      delay(50);
    }
    for (int j = 10; j >= 0; j--) {
      LEDStick.setLEDBrightness(j);
      delay(50);
    }
  }
  //then pulse back to full and exit
  for (int j = 1; j <= 10; j++) {
    LEDStick.setLEDBrightness(j);
    delay(50);
  }
}

void setup() {
  Wire.begin();
  Serial.begin(921600);
  LEDStickOne.begin();
  delay(100);
  setup_wifi();  // Connect to network
  client.setServer(broker, 1883);
  client.setCallback(callback);  // Initialize the callback routine
}

void loop() {
  if (!client.connected())  // Reconnect if connection is lost
  {
    reconnect();
  }
  client.loop();
}
