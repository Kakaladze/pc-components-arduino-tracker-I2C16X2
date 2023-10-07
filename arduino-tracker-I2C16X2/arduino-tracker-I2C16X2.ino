#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

bool connectionInitialized = false;
bool appStarted = false;
uint8_t lastCpuUsage = 0;
uint8_t lastCpuTemp = 0;
uint8_t lastGpuUsage = 0;
uint8_t lastGpuTemp = 0;
uint16_t lastRamMax = 0;
uint16_t lastRamUsage = 0;
uint16_t interval = 2500;

void displayInitScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Waiting for");
  lcd.setCursor(0, 1);  
  lcd.print("deliver app");
}

void handleSerialPortCommunication() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    DynamicJsonDocument doc(200);
    deserializeJson(doc, input);

    if(doc["action"] == "update") {
      if (doc["cpuUsage"]) {
        lastCpuUsage = doc["cpuUsage"];
      }

      if (doc["gpuUsage"]) {
        lastGpuUsage = doc["gpuUsage"];
      }

      if (doc["cpuTemp"]) {
        lastCpuTemp = doc["cpuTemp"];
      }

      if (doc["gpuTemp"]) {
        lastGpuTemp = doc["gpuTemp"];
      }

      if (doc["ramMax"]) {
        lastRamMax = doc["ramMax"];
      }

      if (doc["ramUsage"]) {
        lastRamUsage = doc["ramUsage"];
      }

      connectionInitialized = true;
    }

    if(doc["action"] == "changeInterval") {
      if (doc["interval"] >= 500) {
        interval = doc["interval"];
      }
    }

    if (doc["action"] == "stop") {
      connectionInitialized = false;
      displayInitScreen();
    }

    Serial.println("handled");
  }
}

void displayData(String prefix, uint8_t usage, uint8_t temp) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(prefix + ": Load: " + String(usage) + "%");
    lcd.setCursor(0,1);
    lcd.print(prefix + ": Temp: " + String(temp) + "\337C");
}

void displayRamData(uint16_t max, uint16_t usage) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("RAM: " + String(max) + "MB");
    lcd.setCursor(0,1);
    lcd.print("Usage: " + String(usage) + "MB");
}

void handleDisplayData() {
  static unsigned long lastChangeTime = millis();
  unsigned long currentTime = millis();
  if (connectionInitialized && currentTime - lastChangeTime >= interval) {
    static uint8_t activeScreen = 0;
    if (activeScreen == 0) {
      displayData("CPU", lastCpuUsage, lastCpuTemp);
      activeScreen = 1;
    } 
    else if (activeScreen == 1) {
      displayData("GPU", lastGpuUsage, lastGpuTemp);
      activeScreen = 2;
    }
    else {
      displayRamData(lastRamMax, lastRamUsage);
      activeScreen = 0;
    }
    lastChangeTime = currentTime;
  }
}

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  displayInitScreen();
  Serial.println("init");
}

void loop() {
  handleSerialPortCommunication();
  handleDisplayData();
}