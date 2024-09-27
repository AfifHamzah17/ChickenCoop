#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <RTClib.h>
#include <DHT22.h>
#include <Wire.h>
#include <math.h>

#define LDR_PIN 34
#define PIR_PIN 33
#define RELAY_PIN 25
#define LED_PIN 26
#define CURRENT_SENSOR_PIN 36
#define DHT_PIN 15

RTC_DS3231 rtc;
DHT22 dht(DHT_PIN);

int pirState = 0;
const float voltageSupply = 5.0;
const float rKnown = 2000.0;
const float voltage = 230.0;
const float rl10 = 10.0;
const float gama = 0.7;

#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_PASSWORD ""

const char* server = "api.thingspeak.com";
const String apiKey = "ZBONQ7ZG8E2F00O8";
const unsigned long channelId = 2669844;

void setup_wifi() {
    delay(10);
    Serial.print("Menghubungkan ke ");
    Serial.println(WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi terhubung");
    Serial.print("Alamat IP: ");
    Serial.println(WiFi.localIP());
}

float hitungKecerahan() {
    int nilaiLDR = analogRead(LDR_PIN);
    nilaiLDR = map(nilaiLDR, 4095, 0, 1024, 0);
    nilaiLDR = constrain(nilaiLDR, 0, 1024);
    float voltase = nilaiLDR / 1024.0 * voltageSupply;
    float resistansi = rKnown * voltase / (voltageSupply - voltase);
    return pow((rl10 * pow(10, gama) / resistansi), (1 / gama));
}

float hitungDayaMatahari(float kecerahan) {
    const float efisiensiPanelSurya = 0.15;
    const float luasPanelSurya = 1.0;
    return kecerahan * luasPanelSurya * efisiensiPanelSurya;
}

float readCurrent() {
    int sensorValue = analogRead(CURRENT_SENSOR_PIN);
    float voltageReading = (sensorValue / 4095.0) * 5.0;
    float current = (voltageReading - 2.5) / 0.185;
    return current;
}

float calculatePower(float current) {
    return voltage * current;
}

float calculateLDRLux() {
    int analogValue = analogRead(LDR_PIN);
    float voltageLDR = analogValue / 4096.0 * voltageSupply;
    float resistance = rKnown * voltageLDR / (voltageSupply - voltageLDR);
    return pow((rl10 * pow(10, gama) / resistance), (1 / gama));
}

void kirim_thingspeak(float current, float power, float lampStatus, float solar, float temp) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String url = "http://" + String(server) + "/update?api_key=" + apiKey;
        url += "&field1=" + String(current);
        url += "&field2=" + String(power);
        url += "&field3=" + String(lampStatus);
        url += "&field4=" + String(solar);
        url += "&field5=" + String(temp);
        Serial.print("Meminta URL: ");
        Serial.println(url);
        http.begin(url);
        int httpCode = http.GET();
        if (httpCode > 0) {
            Serial.printf("HTTP GET... kode: %d\n", httpCode);
            if (httpCode == HTTP_CODE_OK) {
                String payload = http.getString();
                Serial.println("Payload respons: " + payload);
            }
        } else {
            Serial.printf("HTTP GET... gagal, error: %s\n", http.errorToString(httpCode).c_str());
        }
        http.end();
    } else {
        Serial.println("WiFi tidak terhubung");
    }
}

bool isNightTime(DateTime now) {
    int hour = now.hour();
    return (hour >= 17 || hour < 6);
}

bool isTemperatureInIdealRange(float temperature) {
    const float lowerLimit = 19;
    const float upperLimit = 29;
    return (temperature >= lowerLimit && temperature <= upperLimit);
}

int calculateLampIntensity(float lux) {
    if (lux >= 200) {
        return 0;
    } else if (lux >= 100) {
        return 50;
    } else if (lux >= 50) {
        return 75;
    } else {
        return 100;
    }
}

void loop() {
    DateTime now = rtc.now();
    pirState = digitalRead(PIR_PIN);
    float lux = calculateLDRLux();
    float current = readCurrent();
    float power = calculatePower(current);
    float solar = hitungDayaMatahari(lux);
    float temperature = dht.getTemperature();
    bool isIdealTemp = isTemperatureInIdealRange(temperature);
    float lampStatus = digitalRead(RELAY_PIN) == HIGH ? 1.0 : 0.0;

    if (isNightTime(now)) {
        if (!isIdealTemp) {
            if (temperature < 19 || lux < 50) {
                int lampIntensity = calculateLampIntensity(lux);
                analogWrite(RELAY_PIN, map(lampIntensity, 0, 100, 0, 255));
                digitalWrite(LED_PIN, HIGH);
            } else if (temperature > 29) {
                digitalWrite(RELAY_PIN, LOW);
                digitalWrite(LED_PIN, LOW);
            }
        }
    } else {
        digitalWrite(RELAY_PIN, LOW);
        digitalWrite(LED_PIN, LOW);
    }

    kirim_thingspeak(current, power, lampStatus, solar, temperature);

    Serial.print("Waktu: ");
    Serial.print(now.hour());
    Serial.print(":");
    Serial.print(now.minute());
    Serial.print(", Lux: ");
    Serial.print(lux);
    Serial.print(", Arus: ");
    Serial.print(current);
    Serial.print(", Daya: ");
    Serial.print(power);
    Serial.print("W, Daya Matahari: ");
    Serial.print(solar);
    Serial.print("W, Suhu: ");
    Serial.print(temperature);
    Serial.println("°C");

    delay(10000);
}
