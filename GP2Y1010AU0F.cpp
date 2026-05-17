#include "GP2Y1010AU0F.h"

GP2Y1010AU0F::GP2Y1010AU0F(uint8_t ledPin, uint8_t measurePin) {
  _LEDPin = ledPin;
  _measurePin = measurePin;
}

bool GP2Y1010AU0F::begin() {
  pinMode(_LEDPin, OUTPUT);
  analogReadResolution(12); // ESP32
  return true;
}

float GP2Y1010AU0F::read() {
  digitalWrite(_LEDPin, LOW);
  delayMicroseconds(_samplingTime);

  int adc = analogRead(_measurePin);

  delayMicroseconds(_deltaTime);
  digitalWrite(_LEDPin, HIGH);
  delayMicroseconds(_sleepTime);

  float voltage = adc * (_VCC / 4095.0);

  float dust = (voltage - 0.098) * 200;   // 0.098 tại quán cafe

  if (dust < 0) dust = 0;

  return dust;
}
