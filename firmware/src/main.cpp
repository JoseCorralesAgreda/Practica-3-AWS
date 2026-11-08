#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <time.h>
#include "secrets.h"

// ESP32 clásico. Confirmar placa y calibrar sin conectar una carga mecánica.
constexpr int PIR_PIN = 27;
constexpr int SERVO_PIN = 18;
constexpr int REST_ANGLE = 0;
constexpr int PRESS_ANGLE = 180;
constexpr uint32_t SERVO_PHASE_MS = 700;
constexpr uint32_t PIR_WARMUP_MS = 60000;
constexpr uint32_t AUTO_COOLDOWN_MS = 60000;
constexpr uint32_t REPORT_MS = 15000;
constexpr uint32_t RETRY_MS = 5000;

class Ambientador {
 public:
  Ambientador() : mqtt(tls) {}

  void begin() {
    Serial.begin(115200);
    pinMode(PIR_PIN, INPUT);
    storageReady = preferences.begin("ambientador", false);
    lastActivation = preferences.getString("activation", "");
    servo.setPeriodHertz(50);
    servo.attach(SERVO_PIN, 500, 2400);
    servo.write(REST_ANGLE);
    topic = String("$aws/things/") + THING_NAME + "/shadow";
    tls.setCACert(ROOT_CA);
    tls.setCertificate(DEVICE_CERT);
    tls.setPrivateKey(PRIVATE_KEY);
    tls.setHandshakeTimeout(3);
    mqtt.setServer(IOT_ENDPOINT, 8883);
    mqtt.setBufferSize(8192);
    mqtt.setSocketTimeout(2);
    mqtt.setCallback([this](char* name, byte* payload, unsigned int length) {
      onMessage(String(name), payload, length);
    });
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    configTime(0, 0, "pool.ntp.org", "time.google.com");
    Serial.println("Inicio; PIR en estabilización durante 60 s.");
  }

  void tick() {
    uint32_t now = millis();
    updateServo(now);
    updateSensor(now);
    // No iniciar conexiones TLS bloqueantes durante un ciclo mecánico.
    if (phase == "idle") connect(now);
    if (mqtt.connected()) {
      mqtt.loop();
      if (!synchronized && now - lastGet >= RETRY_MS) requestShadow();
      if (synchronized && (dirty || now - lastReport >= REPORT_MS) && now - lastPublish >= 200) {
        report(now);
      }
    }
    delay(5);
  }

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
  bool synchronized = false;
  bool dirty = true;
  bool activatedBefore = false;
  uint32_t lastConnect = 0;
  uint32_t lastGet = 0;
  uint32_t lastReport = 0;
  uint32_t lastPublish = 0;
  uint32_t phaseStarted = 0;
  uint32_t lastCycle = 0;
  uint32_t lastVersion = 0;
  uint32_t cycles = 0;

  void connect(uint32_t now) {
    if (mqtt.connected()) return;
    synchronized = false;
    if (now - lastConnect < RETRY_MS) return;
    lastConnect = now;
    if (WiFi.status() != WL_CONNECTED) {
      WiFi.reconnect();
      return;
    }
    // Validar fechas del certificado TLS requiere reloj sincronizado.
    if (time(nullptr) < 1700000000) return;
    if (!mqtt.connect(THING_NAME)) {
      Serial.printf("MQTT no conectado: %d\n", mqtt.state());
      return;
    }
    bool subscribed = true;
    const char* suffixes[] = {"/get/accepted", "/get/rejected", "/update/delta", "/update/accepted", "/update/rejected"};
    for (const char* suffix : suffixes) {
      if (!mqtt.subscribe((topic + suffix).c_str(), 1)) subscribed = false;
    }
    if (!subscribed) {
      mqtt.disconnect();
      return;
    }
    // Una nueva sesión acepta la versión vigente, incluso si se recreó el Shadow.
    lastVersion = 0;
    requestShadow();
    Serial.println("MQTT conectado; solicitando desired pendiente.");
  }

  void requestShadow() {
    mqtt.publish((topic + "/get").c_str(), "{}");
    lastGet = millis();
  }

  void onMessage(const String& name, byte* payload, unsigned int length) {
    // Documento en heap para no consumir la pequeña pila de loopTask.
    DynamicJsonDocument document(16384);
    if (deserializeJson(document, payload, length)) {
      Serial.println("Shadow JSON inválido o demasiado grande.");
      return;
    }
    if (name.endsWith("/get/rejected")) {
      if (document["code"] == 404) {
        synchronized = true;
        dirty = true;
      } else {
        Serial.printf("GET Shadow rechazado: %d\n", document["code"].as<int>());
      }
      return;
    }
    if (name.endsWith("/update/rejected")) {
      Serial.printf("Reporte rechazado: %d\n", document["code"].as<int>());
      dirty = true;
      return;
    }
    if (name.endsWith("/update/accepted")) return;
    uint32_t version = document["version"] | 0UL;
    // Se comparan solo versiones de documentos que contienen desired/delta.
    if (version < lastVersion) return;
    lastVersion = version;
    if (name.endsWith("/get/accepted")) {
      synchronized = true;
      applyDesired(document["state"]["desired"]);
      dirty = true;
    } else if (name.endsWith("/update/delta") && synchronized) {
      applyDesired(document["state"]);
    }
  }

  void applyDesired(JsonVariantConst desired) {
    if (desired["automatic"].is<bool>()) {
      automatic = desired["automatic"].as<bool>();
      dirty = true;
    }
    if (!desired["activationId"].is<const char*>()) return;
    String id = desired["activationId"].as<String>();
    if (id.isEmpty() || id.length() > 128 || id == lastActivation) return;
    // Un comando recibido mientras el servo se mueve queda en desired.
    // Se vuelve a consultar al terminar el ciclo para no perder ese comando.
    if (phase != "idle") return;
    // Guardar ANTES de mover: evita repetir una dosificación tras reiniciar.
    // Un corte en este intervalo puede perder el movimiento: no es exactly-once.
    if (!storageReady || preferences.putString("activation", id) == 0) {
      Serial.println("No se mueve: no fue posible persistir activationId.");
      return;
    }
    lastActivation = id;
    startCycle(millis());
  }

  void updateSensor(uint32_t now) {
    if (!pirReady && now >= PIR_WARMUP_MS) {
      pirReady = true;
      // No considerar el nivel inicial como un flanco de detección nuevo.
      presence = digitalRead(PIR_PIN) == HIGH;
      dirty = true;
    }
    if (!pirReady) return;
    bool reading = digitalRead(PIR_PIN) == HIGH;
    if (reading == presence) return;
    presence = reading;
    dirty = true;
    bool cooldownElapsed = !activatedBefore || now - lastCycle >= AUTO_COOLDOWN_MS;
    if (presence && automatic && synchronized && mqtt.connected() && phase == "idle" && cooldownElapsed) {
      startCycle(now);
    }
  }

  void startCycle(uint32_t now) {
    servo.write(PRESS_ANGLE);
    phase = "pressing";
    phaseStarted = now;
    lastCycle = now;
    activatedBefore = true;
    dirty = true;
    Serial.printf("Inicio ciclo: %lu ms\n", static_cast<unsigned long>(now));
  }

  void updateServo(uint32_t now) {
    if (phase == "idle" || now - phaseStarted < SERVO_PHASE_MS) return;
    phaseStarted = now;
    if (phase == "pressing") {
      servo.write(REST_ANGLE);
      phase = "returning";
    } else {
      phase = "idle";
      cycles++;
      if (mqtt.connected()) requestShadow();
    }
    dirty = true;
  }

  void report(uint32_t now) {
    StaticJsonDocument<1024> document;
    JsonObject reported = document.createNestedObject("state").createNestedObject("reported");
    reported["presence"] = presence;
    reported["pirReady"] = pirReady;
    reported["automatic"] = automatic;
    reported["activationId"] = lastActivation;
    reported["servoState"] = phase;
    reported["servoAngle"] = phase == "pressing" ? PRESS_ANGLE : REST_ANGLE;
    reported["cyclesSinceBoot"] = cycles;
    reported["uptimeSeconds"] = now / 1000;
    reported["sampledAt"] = static_cast<uint32_t>(time(nullptr));
    char payload[1024];
    size_t length = serializeJson(document, payload, sizeof(payload));
    lastPublish = now;
    // QoS 0: el siguiente reporte periódico repara una publicación perdida.
    if (mqtt.publish((topic + "/update").c_str(), payload, length)) {
      lastReport = now;
      dirty = false;
    }
  }
};

Ambientador ambientador;
void setup() { ambientador.begin(); }
void loop() { ambientador.tick(); }
