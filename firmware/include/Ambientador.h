#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

class Ambientador {
 public:
  Ambientador();
  void begin();
  void tick();

 private:
  WiFiClientSecure tls;
  PubSubClient mqtt;
  Servo servo;
  Preferences preferences;
  String topic;
  String lastActivation;
  String phase = "idle";
  bool storageReady = false;
  bool automatic = false;
  bool presence = false;
  bool pirReady = false;
  bool pirRaw = false;
  bool pirRawInitialized = false;
  bool synchronized = false;
  bool dirty = true;
  bool activatedBefore = false;
  uint32_t lastConnect = 0;
  uint32_t lastGet = 0;
  uint32_t lastReport = 0;
  uint32_t lastPirLog = 0;
  uint32_t lastPublish = 0;
  uint32_t phaseStarted = 0;
  uint32_t lastCycle = 0;
  uint32_t lastVersion = 0;
  uint32_t cycles = 0;


  void connect(uint32_t now);
  void requestShadow();
  void onMessage(const String& name, byte* payload, unsigned int length);
  void applyDesired(JsonVariantConst desired);
  void updateSensor(uint32_t now);
  void startCycle(uint32_t now);
  void updateServo(uint32_t now);
  void report(uint32_t now);
};
