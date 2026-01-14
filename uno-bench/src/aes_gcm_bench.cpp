#include <Arduino.h>
#include <AES.h>
#include <GCM.h>

// -----------------------------
// CONFIG
// -----------------------------
static const uint32_t BAUD = 115200;
static const size_t SIZES[] = {16, 32, 64, 128, 256};
static const size_t NSIZES = sizeof(SIZES) / sizeof(SIZES[0]);
static const uint16_t REPS = 200;

// -----------------------------
// BUFFERS
// -----------------------------
static uint8_t KEY_16[16]   = {0};
static uint8_t NONCE_12[12] = {0}; // Standard 12-byte IV for GCM
static uint8_t AAD[16]      = {0};

static uint8_t PT[256];
static uint8_t CT[256];
static uint8_t TAG[16];

// -----------------------------
// HELPERS
// -----------------------------
static inline uint32_t now_us() { return micros(); }
static inline uint32_t us_to_cycles(uint32_t us) { return us * 16UL; }

static void fill_inputs() {
  for (size_t i = 0; i < sizeof(PT); i++) PT[i] = (uint8_t)(i & 0xFF);
  for (size_t i = 0; i < sizeof(AAD); i++) AAD[i] = (uint8_t)(0xA0 + i);
  for (size_t i = 0; i < sizeof(KEY_16); i++) KEY_16[i] = (uint8_t)(0x10 + i);
  for (size_t i = 0; i < sizeof(NONCE_12); i++) NONCE_12[i] = (uint8_t)(0x20 + i);
}

// -----------------------------
// BENCHMARK: AES-GCM
// -----------------------------
static uint32_t bench_aes_gcm(size_t mlen) {
  GCM<AES128> gcm;
  uint32_t t0 = now_us();

  for (uint16_t i = 0; i < REPS; i++) {
    gcm.clear();
    gcm.setKey(KEY_16, sizeof(KEY_16));
    gcm.setIV(NONCE_12, sizeof(NONCE_12));
    gcm.addAuthData(AAD, sizeof(AAD));
    gcm.encrypt(CT, PT, mlen);
    gcm.computeTag(TAG, sizeof(TAG));
  }

  return now_us() - t0;
}

// -----------------------------
// ENTRYPOINT
// -----------------------------
void setup() {
  Serial.begin(BAUD);
  fill_inputs();
  delay(200);

  Serial.println(F("algo,msg_len,reps,total_us,avg_us,approx_cycles"));

  for (size_t si = 0; si < NSIZES; si++) {
    size_t mlen = SIZES[si];

    uint32_t total_us = bench_aes_gcm(mlen);
    float avg_us = (float)total_us / (float)REPS;

    Serial.print(F("AES-GCM,"));
    Serial.print(mlen); Serial.print(F(","));
    Serial.print(REPS); Serial.print(F(","));
    Serial.print(total_us); Serial.print(F(","));
    Serial.print(avg_us, 3); Serial.print(F(","));
    Serial.println(us_to_cycles((uint32_t)avg_us));
  }

  Serial.println(F("# Done"));
}

void loop() {}