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
const char* serverUrl = "http://192.168.10.103:5000/api/hardware";

// --- CẤU HÌNH CÁC CHÂN PIN (GPIO) ---
#define DHTPIN 4          // Chân nối với cảm biến DHT11/22
#define DHTTYPE DHT11    // Đổi thành DHT22 nếu bạn dùng loại trắng
#define SOIL_PIN 32       // ĐỔI sang GPIO32 (hỗ trợ pull-down nội bộ)
#define WATER_PIN 33      // ĐỔI sang GPIO33 (hỗ trợ pull-down nội bộ)
#define PUMP_PIN 2        // Chân điều khiển Relay

DHT dht(DHTPIN, DHTTYPE);

// --- HÀM PHÁT HIỆN PIN FLOATING (không cắm sensor) ---
// Đọc 20 lần, nếu max-min > threshold thì pin đang nổi (floating)
bool isFloating(uint8_t pin, int samples, int threshold) {
  int minVal = 4095, maxVal = 0;
  for (int i = 0; i < samples; i++) {
    int v = analogRead(pin);
    if (v < minVal) minVal = v;
    if (v > maxVal) maxVal = v;
    delay(5);
  }
  return (maxVal - minVal) > threshold;
}

// --- LẤY TRUNG BÌNH NHIỀU LẦN ĐỌC ---
int avgRead(uint8_t pin, int samples) {
  long s = 0;
  for (int i = 0; i < samples; i++) { s += analogRead(pin); delay(10); }
  return s / samples;
}

// --- KIỂM TRA TRẠNG THÁI KẾT NỐI SENSOR ---
void checkSensors() {
  Serial.println("\n========== KIEM TRA CAM BIEN ==========");

  // Kiểm tra DHT11
  float testT = dht.readTemperature();
  float testH = dht.readHumidity();
  if (isnan(testT) || isnan(testH)) {
    Serial.println("[X] DHT11               : KHONG KET NOI!");
  } else {
    Serial.printf("[OK] DHT11              : %.1fC | Do am KK: %.1f%%\n", testT, testH);
  }

  // Kiểm tra cảm biến độ ẩm đất (GPIO 34) - dùng variance
  if (isFloating(SOIL_PIN, 20, 300)) {
    Serial.println("[X] Cam bien do am dat  : KHONG KET NOI (pin noi)!");
  } else {
    int raw = avgRead(SOIL_PIN, 10);
    float pct = constrain(map(raw, 0, 4095, 0, 100), 0, 100);
    Serial.printf("[OK] Cam bien do am dat : Do am dat = %.1f%%\n", pct);
  }

  // Kiểm tra cảm biến mực nước (GPIO 35) - dùng variance
  if (isFloating(WATER_PIN, 20, 300)) {
    Serial.println("[X] Cam bien muc nuoc   : KHONG KET NOI (pin noi)!");
  } else {
    int raw = avgRead(WATER_PIN, 10);
    float pct = constrain(map(raw, 0, 4095, 0, 100), 0, 100);
    Serial.printf("[OK] Cam bien muc nuoc  : Muc nuoc = %.1f%%\n", pct);
  }

  Serial.println("[OK] Relay (GPIO2)      : San sang dieu khien");
  Serial.println("======================================\n");
}

void setup() {
  Serial.begin(115200);
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW); // Đảm bảo máy bơm tắt khi khởi động

  dht.begin();
  delay(2000); // DHT11 cần 2 giây để ổn định sau khi khởi động

  // Kích hoạt điện trở kéo xuống nội bộ - không cần điện trở ngoài!
  pinMode(SOIL_PIN,  INPUT_PULLDOWN);
  pinMode(WATER_PIN, INPUT_PULLDOWN);
  delay(100);

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

  // Kiểm tra tất cả cảm biến sau khi WiFi kết nối
  checkSensors();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // 1. Đọc dữ liệu từ cảm biến
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    // Lấy trung bình 10 lần đọc để lọc nhiễu ADC (cảm biến 2 dây rất dễ bị nhiễu)
    long soilSum = 0, waterSum = 0;
    for (int i = 0; i < 10; i++) {
      soilSum  += analogRead(SOIL_PIN);
      waterSum += analogRead(WATER_PIN);
      delay(10); // Nghỉ 10ms giữa mỗi lần đọc
    }
    int soilRaw  = soilSum  / 10;
    int waterRaw = waterSum / 10;

    // --- HIỆU CHỈNH THÔNG MINH ---
    // Số RAW khi đất KHÔ (thường là số cao khi dùng pull-down nội bộ)
    static int rawKho = 3440; 
    // Số RAW khi đất ƯỚT (thường là số thấp hơn)
    static int rawUot = 1000; 

    // Tự động cập nhật mốc nếu thấy số cực đoan hơn (Auto-calibrate)
    if (soilRaw > rawKho) rawKho = soilRaw;
    if (soilRaw < rawUot && soilRaw > 50) rawUot = soilRaw;

    float soilPct = constrain(map(soilRaw, rawKho, rawUot, 0, 100), 0, 100);
    float waterPct = constrain(map(waterRaw, 0, 4095, 0, 100), 0, 100);

    // --- In trạng thái kết nối mỗi chu kỳ ---
    Serial.println("--- Trang thai cam bien ---");
    bool dhtOk = true;
    if (isnan(t) || isnan(h)) {
      Serial.println(" [X] DHT11: KHONG KET NOI!");
      t = -1;  // Đánh dấu lỗi
      h = -1;
      dhtOk = false;
    } else {
      Serial.printf(" [OK] DHT11        : Nhiet do=%.1fC  Do am KK=%.1f%%\n", t, h);
    }

    bool soilOk = true;
    int soilActualRaw = avgRead(SOIL_PIN, 10);
    // Tăng threshold lên 800 để bớt nhạy với nhiễu môi trường
    if (isFloating(SOIL_PIN, 20, 800)) {
      Serial.printf(" [X] Cam bien dat : CHUA CAM (Nhiễu RAW=%d)\n", soilActualRaw);
      soilPct = -1;
      soilOk = false;
    } else {
      Serial.printf(" [OK] Cam bien dat : Do am=%.1f%% (RAW=%d)\n", soilPct, soilRaw);
    }

    bool waterOk = true;
    int waterActualRaw = avgRead(WATER_PIN, 10);
    if (isFloating(WATER_PIN, 20, 800)) {
      Serial.printf(" [X] Cam bien nuoc: CHUA CAM (Nhiễu RAW=%d)\n", waterActualRaw);
      waterPct = -1;
      waterOk = false;
    } else {
      Serial.printf(" [OK] Cam bien nuoc: Muc nuoc=%.1f%% (RAW=%d)\n", waterPct, waterRaw);
    }
    Serial.println("---------------------------");

    // 2. Gửi dữ liệu lên Server (Flask AI)
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Tạo chuỗi JSON
    StaticJsonDocument<300> doc;
    doc["temp"] = t;
    doc["humidity"] = h;
    doc["soil_moisture"] = soilPct;
    doc["water_level"] = waterPct;
    // Gửi thêm thông tin sensor nào đang sống
    doc["dht_ok"] = dhtOk;
    doc["soil_ok"] = soilOk;
    doc["water_ok"] = waterOk;

    String requestBody;
    serializeJson(doc, requestBody);

    int httpResponseCode = http.POST(requestBody);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Phan hoi tu AI Server: " + response);

      // 3. Xử lý lệnh tưới từ Server
      StaticJsonDocument<256> resDoc;
      DeserializationError error = deserializeJson(resDoc, response);
      
      if (!error) {
        bool pumpOn = resDoc["pump_on"];
        float durationMinutes = resDoc["irrigation_duration"];

        if (pumpOn && durationMinutes > 0) {
          float durationSeconds = durationMinutes * 60;
          Serial.printf("AI Brain Decision: BAT MAY BOM trong %.1f giay (%.2f phut)\n", durationSeconds, durationMinutes);
          
          digitalWrite(PUMP_PIN, HIGH);
          // Tưới trong thời gian quy định
          delay(durationSeconds * 1000); 
          digitalWrite(PUMP_PIN, LOW);
          
          Serial.println(">> Hoan thanh chu ky tuoi AI.");
        } else {
          Serial.println("AI Brain Decision: Tat / Khong can tuoi.");
          digitalWrite(PUMP_PIN, LOW);
        }
      } else {
        Serial.print("Loi giai ma JSON: ");
        Serial.println(error.c_str());
      }
    } else {
      Serial.print("Loi ket noi server: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }

  // Đợi 5 giây trước khi chu kỳ tiếp theo
  delay(5000);
}
