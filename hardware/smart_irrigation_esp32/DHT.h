/*!
 * @file DHT.h
 * Header-only DHT sensor library (DHT11 / DHT22 / AM2302)
 * Bundled locally for Arduino sketch compatibility.
 * Based on Adafruit DHT library (MIT license).
 */

#ifndef DHT_H
#define DHT_H

#include "Arduino.h"

#define DHT11  11
#define DHT12  12
#define DHT21  21
#define DHT22  22
#define AM2301 21
#define AM2302 22

#define MIN_INTERVAL 2000UL
#define DHT_TIMEOUT  UINT32_MAX

// ── InterruptLock helper ──────────────────────────────────────────────────────
class InterruptLock {
public:
  InterruptLock()  { noInterrupts(); }
  ~InterruptLock() { interrupts();   }
};

// ── DHT class ─────────────────────────────────────────────────────────────────
class DHT {
public:
  // Constructor
  DHT(uint8_t pin, uint8_t type, uint8_t count = 6)
    : _pin(pin), _type(type), _lastresult(false),
      _lastreadtime(0), pullTime(55)
  {
    (void)count;
    _maxcycles = microsecondsToClockCycles(1000);
  }

  // Initialise sensor pin
  void begin(uint8_t usec = 55) {
    pinMode(_pin, INPUT_PULLUP);
    _lastreadtime = millis() - MIN_INTERVAL;
    pullTime = usec;
  }

  // Unit conversions
  float convertCtoF(float c) { return c * 1.8f + 32.0f; }
  float convertFtoC(float f) { return (f - 32.0f) * 0.55556f; }

  // Read humidity (%)
  float readHumidity(bool force = false) {
    float f = NAN;
    if (read(force)) {
      switch (_type) {
        case DHT11:
        case DHT12:
          f = data[0] + data[1] * 0.1f;
          break;
        case DHT22:
        case DHT21:
          f = ((uint16_t)data[0] << 8 | data[1]) * 0.1f;
          break;
      }
    }
    return f;
  }

  // Read temperature (Celsius by default, Fahrenheit if S=true)
  float readTemperature(bool S = false, bool force = false) {
    float f = NAN;
    if (read(force)) {
      switch (_type) {
        case DHT11:
          f = data[2];
          if (data[3] & 0x80) f = -1 - f;
          f += (data[3] & 0x0F) * 0.1f;
          if (S) f = convertCtoF(f);
          break;
        case DHT12:
          f = data[2] + (data[3] & 0x0F) * 0.1f;
          if (data[2] & 0x80) f *= -1;
          if (S) f = convertCtoF(f);
          break;
        case DHT22:
        case DHT21:
          f = ((uint16_t)(data[2] & 0x7F) << 8 | data[3]) * 0.1f;
          if (data[2] & 0x80) f *= -1;
          if (S) f = convertCtoF(f);
          break;
      }
    }
    return f;
  }

  // Compute heat index
  float computeHeatIndex(float temperature, float percentHumidity,
                         bool isFahrenheit = true) {
    if (!isFahrenheit) temperature = convertCtoF(temperature);
    float hi = 0.5f * (temperature + 61.0f +
                       ((temperature - 68.0f) * 1.2f) +
                       (percentHumidity * 0.094f));
    if (hi > 79.0f) {
      hi = -42.379f
           + 2.04901523f   * temperature
           + 10.14333127f  * percentHumidity
           - 0.22475541f   * temperature * percentHumidity
           - 0.00683783f   * temperature * temperature
           - 0.05481717f   * percentHumidity * percentHumidity
           + 0.00122874f   * temperature * temperature * percentHumidity
           + 0.00085282f   * temperature * percentHumidity * percentHumidity
           - 0.00000199f   * temperature * temperature
                           * percentHumidity * percentHumidity;

      if ((percentHumidity < 13.0f) &&
          (temperature >= 80.0f) && (temperature <= 112.0f))
        hi -= ((13.0f - percentHumidity) * 0.25f) *
              sqrt((17.0f - abs(temperature - 95.0f)) * 0.05882f);
      else if ((percentHumidity > 85.0f) &&
               (temperature >= 80.0f) && (temperature <= 87.0f))
        hi += ((percentHumidity - 85.0f) * 0.1f) *
              ((87.0f - temperature) * 0.2f);
    }
    return isFahrenheit ? hi : convertFtoC(hi);
  }

  // Low-level read – returns true if checksum passes
  bool read(bool force = false) {
    uint32_t currenttime = millis();
    if (!force && ((currenttime - _lastreadtime) < MIN_INTERVAL))
      return _lastresult;
    _lastreadtime = currenttime;

    data[0] = data[1] = data[2] = data[3] = data[4] = 0;

    #if defined(ESP8266) || defined(ESP32)
      yield();
    #endif

    // Pull high, then low to signal start
    pinMode(_pin, INPUT_PULLUP);
    delay(1);
    pinMode(_pin, OUTPUT);
    digitalWrite(_pin, LOW);

    switch (_type) {
      case DHT22:
      case DHT21:
        delayMicroseconds(1100);
        break;
      default:            // DHT11 / DHT12
        delay(20);
        break;
    }

    uint32_t cycles[80];
    {
      pinMode(_pin, INPUT_PULLUP);
      delayMicroseconds(pullTime);
      InterruptLock lock;

      if (expectPulse(LOW)  == DHT_TIMEOUT) { _lastresult = false; return false; }
      if (expectPulse(HIGH) == DHT_TIMEOUT) { _lastresult = false; return false; }

      for (int i = 0; i < 80; i += 2) {
        cycles[i]     = expectPulse(LOW);
        cycles[i + 1] = expectPulse(HIGH);
      }
    }

    for (int i = 0; i < 40; ++i) {
      uint32_t lo = cycles[2 * i];
      uint32_t hi = cycles[2 * i + 1];
      if (lo == DHT_TIMEOUT || hi == DHT_TIMEOUT) {
        _lastresult = false;
        return false;
      }
      data[i / 8] <<= 1;
      if (hi > lo) data[i / 8] |= 1;
    }

    _lastresult =
      (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF));
    return _lastresult;
  }

private:
  uint8_t  data[5];
  uint8_t  _pin, _type;
  uint32_t _lastreadtime, _maxcycles;
  bool     _lastresult;
  uint8_t  pullTime;

  uint32_t expectPulse(bool level) {
    uint32_t count = 0;
    while (digitalRead(_pin) == level) {
      if (count++ >= _maxcycles) return DHT_TIMEOUT;
    }
    return count;
  }
};

#endif // DHT_H
