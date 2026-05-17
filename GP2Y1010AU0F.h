#ifndef GP2Y1010AU0F_H
#define GP2Y1010AU0F_H

#include "Arduino.h"

class GP2Y1010AU0F {
  private:
    uint8_t        _LEDPin;
    uint8_t        _measurePin;
    int            _samplingTime     = 280;
    int            _deltaTime        = 40;
    int            _sleepTime        = 9680;
    float          _VCC              = 3.3;

  public:
    GP2Y1010AU0F(uint8_t ledPin, uint8_t measurePin);
    bool begin();
    float read();
};

#endif /* GP2Y1010AU0F_H */
