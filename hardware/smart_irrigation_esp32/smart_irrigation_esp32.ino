/*
 * HỆ THỐNG TƯỚI CÂY THÔNG MINH AI (ESP32 FIRMWARE)
 * -----------------------------------------------
 * Nhiệm vụ: Đọc cảm biến và nhận lệnh từ Flask AI Backend qua Wifi.
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "DHT.h"

// --- CẤU HÌNH WIFI (BẠN HÃY SỬA LẠI ĐÚNG VỚI WIFI NHÀ MÌNH) ---
const char* ssid = "Duykhang2";
const char* password = "Comtam@456";

// --- ĐỊA CHỈ SERVER (HÃY SỬA IP THEO MÁY TÍNH CHẠY APP.PY) ---
// Ví dụ: http://192.168.1.5:5000/api/hardware
const char* serverUrl = "http://192.168.10.:5000/api/hardware";

// --- CẤU HÌNH CÁC CHÂN PIN (GPIO) ---
#define DHTPIN 4          // Chân nối với cảm biến DHT11/22
#define DHTTYPE DHT11    // Đổi thành DHT22 nếu bạn dùng loại trắng
#define SOIL_PIN 34       // Chân Analog nối với cảm biến độ ẩm đất
#define WATER_PIN 35      // Chân Analog nối với cảm biến mực nước (MỚI)
#define PUMP_PIN 2        // Chân điều khiển Relay

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW); // Đảm bảo máy bơm tắt khi khởi động

  dht.begin();

  // Kết nối Wifi
  Serial.print("Dang ket noi Wifi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Wifi da ket noi!");
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // 1. Đọc dữ liệu từ cảm biến
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    int soilRaw = analogRead(SOIL_PIN);
    int waterRaw = analogRead(WATER_PIN);
    
    // Chuyển đổi giá trị Analog sang %
    float soilPct = map(soilRaw, 4095, 0, 0, 100);
    float waterPct = map(waterRaw, 0, 4095, 0, 100); // 0 là cạn, 4095 là đầy (Tùy loại cảm biến)

    if (isnan(t) || isnan(h)) {
      Serial.println("Loi doc cam bien DHT!");
      return;
    }

    Serial.printf("Temp: %.1fC, Humid: %.1f%%, Soil: %.1f%%\n", t, h, soilPct);

    // 2. Gửi dữ liệu lên Server (Flask AI)
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Tạo chuỗi JSON
    StaticJsonDocument<200> doc;
    doc["temp"] = t;
    doc["humidity"] = h;
    doc["soil_moisture"] = soilPct;
    doc["water_level"] = waterPct;

    String requestBody;
    serializeJson(doc, requestBody);

    int httpResponseCode = http.POST(requestBody);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Phan hoi tu AI Server: " + response);

      // 3. Xử lý lệnh tưới từ Server
      StaticJsonDocument<200> resDoc;
      deserializeJson(resDoc, response);
      
      float duration = resDoc["irrigation_duration"];
      bool pumpOn = resDoc["pump_on"];

      if (pumpOn && duration > 0) {
        Serial.printf("AI ra lenh: Bat may bom trong %.2f phut\n", duration);
        digitalWrite(PUMP_PIN, HIGH);
        
        // Tưới trong thời gian quy định (đổi từ phút sang miligiây)
        // Lưu ý: delay lớn sẽ làm ESP32 treo, trong thực tế nên dùng millis()
        delay(duration * 60 * 1000); 
        
        digitalWrite(PUMP_PIN, LOW);
        Serial.println("Da tuoi xong!");
      } else {
        Serial.println("AI: Dat du am, khong can tuoi.");
        digitalWrite(PUMP_PIN, LOW);
      }
    } else {
      Serial.print("Loi ket noi server: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }

  // Đợi 30 giây trước khi chu kỳ tiếp theo
  delay(30000);
}
