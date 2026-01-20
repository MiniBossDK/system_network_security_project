#include <avr/sleep.h>
#include <Arduino.h>

// =============================================================
// SETUP (Runs ONCE per board reset)
// =============================================================
void setup() {
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    sleep_cpu();
}

void loop() {
  // Do nothing
}