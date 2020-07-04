/*
  SimpleMQTTClient.ino
  The purpose of this exemple is to illustrate a simple handling of MQTT and Wifi connection.
  Once it connects successfully to a Wifi network and a MQTT broker, it subscribe to a topic and send a message to it.
  It will also send a message delayed 5 seconds later.
*/
#include "SPI.h"
#include "TFT_22_ILI9225.h"
#include "EspMQTTClient.h"
#include <../fonts/FreeSans12pt7b.h>
#include <../fonts/FreeSans24pt7b.h>
#include <../fonts/FreeSerifItalic9pt7b.h>
#include <../fonts/FreeMonoBold9pt7b.h>
#include <../fonts/FreeSansBold9pt7b.h>


#if defined (ARDUINO_ARCH_STM32F1)
#define TFT_RST PA1
#define TFT_RS  PA2
#define TFT_CS  PA0 // SS
#define TFT_SDI PA7 // MOSI
#define TFT_CLK PA5 // SCK
#define TFT_LED 0 // 0 if wired to +5V directly
#elif defined(ESP8266)
#define TFT_RST 4   // D2
#define TFT_RS  5   // D1
#define TFT_CLK 14  // D5 SCK
//#define TFT_SDO 12  // D6 MISO
#define TFT_SDI 13  // D7 MOSI
#define TFT_CS  15  // D8 SS
#define TFT_LED 2   // D4     set 0 if wired to +5V directly -> D3=0 is not possible !!
#elif defined(ESP32)
#define TFT_RST 26  // IO 26
#define TFT_RS  25  // IO 25
#define TFT_CLK 14  // HSPI-SCK
//#define TFT_SDO 12  // HSPI-MISO
#define TFT_SDI 13  // HSPI-MOSI
#define TFT_CS  15  // HSPI-SS0
#define TFT_LED 0 // 0 if wired to +5V directly
#else
#define TFT_RST 8
#define TFT_RS  9
#define TFT_CS  10  // SS
#define TFT_SDI 11  // MOSI
#define TFT_CLK 13  // SCK
#define TFT_LED 3   // 0 if wired to +5V directly
#endif
#define TFT_BRIGHTNESS 200 
TFT_22_ILI9225 tft = TFT_22_ILI9225(TFT_RST, TFT_RS, TFT_CS, TFT_LED, TFT_BRIGHTNESS);


int16_t x=0, y=0, w, h;
String inString = ""; 
String inString2 = "";
 int scan;
 String input1 ="hasend/power1";
String input2 ="hasend/power2";

EspMQTTClient client(
  "ORBI55",
  "***",
  "192.168.5.64",  // MQTT Broker server ip
  "abhinav",   // Can be omitted if not needed
  "***",   // Can be omitted if not needed
  "ili",     // Client name that uniquely identify your device
  1883              // The MQTT port, default to 1883. this line can be omitted
);

void setup()
{
  Serial.begin(115200);

  // Optionnal functionnalities of EspMQTTClient : 
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").
  client.enableLastWillMessage("TestClient/lastwill", "I am going offline");  // You can activate the retain flag by setting the third parameter to true
       tft.begin();
        tft.setOrientation(0);
       tft.setGFXFont(&FreeSansBold9pt7b); // Set current font

}


void onConnectionEstablished()
{
  // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe("hasend/power1", [](const String & payload) {
    Serial.println(payload);
      // Draw third string in same font
  String s2 = ("Phase1:    " +payload +"W"); // Create string object
  tft.setGFXFont(&FreeSansBold9pt7b); // Set current font
  tft.getGFXTextExtent(s2, x, y, &w, &h); // Get string extents 
  tft.setOrientation(0);
  tft.fillRectangle(0, 42, tft.maxX(), 68, COLOR_BEIGE);
 tft.drawGFXText(5, 62, s2, COLOR_RED); // Print string
  });

  client.subscribe("hasend/power2", [](const String & topic, const String & payload) {
    Serial.println(topic + ": " + payload);
 
  String s3 = ("Phase2:    " +payload +"W"); // Create string object
  tft.setGFXFont(&FreeSansBold9pt7b); // Set current font
  tft.getGFXTextExtent(s3, x, y, &w, &h); // Get string extents
  tft.setOrientation(0);
  tft.fillRectangle(0, 69, tft.maxX(), 93, COLOR_BEIGE);
  
 tft.drawGFXText(5, 85, s3, COLOR_RED); // Print string
  });

  client.subscribe("hasend/energydly", [](const String & topic, const String & payload) {
    Serial.println(topic + ": " + payload);

  String s4 = ("Today: " +payload +"kWH"); // Create string object
  tft.setOrientation(0);
  tft.setGFXFont(&FreeSansBold9pt7b); // Set current font
  tft.getGFXTextExtent(s4, x, y, &w, &h); // Get string extents
  tft.fillRectangle(0, 95, tft.maxX(), 123, COLOR_SNOW);
  tft.drawRectangle(0,94,tft.maxX(), 149, COLOR_GREEN);
  tft.drawGFXText(5, 113, s4, COLOR_BLUEVIOLET); // Print string
  });


 
  client.subscribe("hasend/energymnthly", [](const String & topic, const String & payload) {
    Serial.println(topic + ": " + payload);

  String s5 = ("Month: " +payload +"kWH"); // Create string object
  tft.setGFXFont(&FreeSansBold9pt7b); // Set current font
  tft.getGFXTextExtent(s5, x, y, &w, &h); // Get string extents
  tft.setOrientation(0);
  tft.drawRectangle(0,94,tft.maxX(), 149, COLOR_GREEN);
  tft.fillRectangle(1, 124, tft.maxX(), 148, COLOR_SNOW);
 tft.drawGFXText(5, 140, s5, COLOR_BLUEVIOLET); // Print string
  });

  
  client.subscribe("hasend/tempodr", [](const String & topic, const String & payload) {
    Serial.println(topic + ": " + payload);

  String s6 = ("Outdoor:    " +payload +"C"); // Create string object
  tft.setOrientation(0);
  tft.fillRectangle(0, 150, tft.maxX(), 172, COLOR_LIGHTCYAN);
  tft.drawGFXText(5, 168, s6, COLOR_BLACK); // Print string
  });

  
  client.subscribe("hasend/tempindr", [](const String & topic, const String & payload) {
    Serial.println(topic + ": " + payload);

  String s7 = ("House:      " +payload +"C"); // Create string object
  tft.setOrientation(0);
  tft.fillRectangle(0, 173, tft.maxX(), 199, COLOR_LIGHTCYAN);
 tft.drawGFXText(5, 192, s7, COLOR_BLACK); // Print string
  });

  
  client.subscribe("hasend/tempbr", [](const String & topic, const String & payload) {
    Serial.println(topic + ": " + payload);

  String s8 = ("Bedroom:    " +payload +"C"); // Create string object
  tft.setOrientation(0);
  tft.fillRectangle(0, 200, tft.maxX(), tft.maxY(), COLOR_AZUR);
  tft.drawGFXText(5, 216, s8, COLOR_BLACK); // Print string
  });  

  client.subscribe("hasend/tempowm", [](const String & topic, const String & payload) {
    Serial.println(topic + ": " + payload);

  String s10 = ("Weather:   " +payload +"C"); // Create string object
  tft.setOrientation(0);
  tft.fillRectangle(0, 0, tft.maxX(), 20, COLOR_AZUR);
  
  tft.drawGFXText(5, 16, s10, COLOR_NAVY); // Print string
  });  

    client.subscribe("hasend/conditionowm", [](const String & topic, const String & payload) {
    Serial.println(topic + ": " + payload);

  String s9 = (payload); // Create string object
  tft.setOrientation(0);
  tft.fillRectangle(0, 21, tft.maxX(), 40, COLOR_AZUR);
  tft.drawLine(0, 41, tft.maxX(), 41, COLOR_RED);
  tft.drawGFXText(5, 34, s9, COLOR_NAVY); // Print string
  }); 
  // Publish a message to "mytopic/test"
  client.publish("mytopic/test", "This is a message"); // You can activate the retain flag by setting the third parameter to true
  }



void loop()
{
  client.loop();
}
