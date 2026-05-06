#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <TinyGPSPlus.h>

// ---------------- WIFI ----------------
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";

// Raspberry Pi endpoint (change PI IP)
String SERVER_URL = "http://192.168.1.50:5000/api/telemetry";

// ---------------- SENSORS PINS ----------------
#define DHTPIN 4
#define DHTTYPE DHT11

const int MQ2_PIN = 34;     // Gas analog
const int MQ3_PIN = 35;     // Alcohol analog
const int MIC_PIN = 32;     // Mic analog

// GPS on UART2
HardwareSerial GPS_Serial(2);
TinyGPSPlus gps;

// ---------------- OBJECTS ----------------
DHT dht(DHTPIN, DHTTYPE);

// ---------------- HELPERS ----------------
int readAnalogAverage(int pin, int samples = 20) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(2);
  }
  return (int)(sum / samples);
}

// Simple mic “level” (peak-to-peak) for short window
int readMicLevel(int pin, int msWindow = 50) {
  unsigned long start = millis();
  int minVal = 4095;
  int maxVal = 0;
  while (millis() - start < (unsigned long)msWindow) {
    int v = analogRead(pin);
    if (v < minVal) minVal = v;
    if (v > maxVal) maxVal = v;
  }
  return maxVal - minVal; // higher = louder
}

void setup() {
  Serial.begin(115200);

  // ADC settings (optional)
  analogReadResolution(12); // 0-4095

  dht.begin();

  // GPS serial: RX=16, TX=17 (ESP32)
  GPS_Serial.begin(9600, SERIAL_8N1, 16, 17);

  // WiFi connect
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // -------- Read GPS continuously for a moment --------
  unsigned long gpsStart = millis();
  while (millis() - gpsStart < 1200) {
    while (GPS_Serial.available() > 0) {
      gps.encode(GPS_Serial.read());
    }
  }

  double lat = 0.0, lon = 0.0;
  float speedKmph = 0.0;

  if (gps.location.isValid()) {
    lat = gps.location.lat();
    lon = gps.location.lng();
  }
  if (gps.speed.isValid()) {
    speedKmph = gps.speed.kmph();
  }

  // -------- Read DHT --------
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // Celsius

  // If DHT fails, keep as null-like
  bool dhtOk = !(isnan(h) || isnan(t));

  // -------- Read analog sensors --------
  int mq2 = readAnalogAverage(MQ2_PIN);
  int mq3 = readAnalogAverage(MQ3_PIN);
  int micLevel = readMicLevel(MIC_PIN);

  // -------- Build JSON --------
  String json = "{";
  json += "\"device_id\":\"esp32-bb-01\",";
  if (dhtOk) {
    json += "\"temperature\":" + String(t, 2) + ",";
    json += "\"humidity\":" + String(h, 2) + ",";
  } else {
    json += "\"temperature\":null,";
    json += "\"humidity\":null,";
  }
  json += "\"mq2_gas\":" + String(mq2) + ",";
  json += "\"mq3_alcohol\":" + String(mq3) + ",";
  json += "\"mic_level\":" + String(micLevel) + ",";
  json += "\"latitude\":" + String(lat, 6) + ",";
  json += "\"longitude\":" + String(lon, 6) + ",";
  json += "\"speed_kmph\":" + String(speedKmph, 2);
  json += "}";

  Serial.println("Sending: " + json);

  // -------- Send to Raspberry Pi --------
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(json);
    String payload = http.getString();

    Serial.print("HTTP Code: ");
    Serial.println(httpCode);
    Serial.print("Response: ");
    Serial.println(payload);

    http.end();
  } else {
    Serial.println("WiFi disconnected!");
  }

  delay(5000); // send every 5 seconds
}