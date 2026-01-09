#include <Arduino.h>
#include <AES.h>
#include <GCM.h>

extern "C" int crypto_aead_encrypt(
  unsigned char *c, unsigned long long *clen,
  const unsigned char *m, unsigned long long mlen,
  const unsigned char *ad, unsigned long long adlen,
  const unsigned char *nsec,
  const unsigned char *npub,
  const unsigned char *k
);


// -----------------------------
// CONFIG
// -----------------------------
static const uint32_t BAUD = 115200;

// Test message sizes (bytes)
static const size_t SIZES[] = {16, 32, 64, 128, 256};
static const size_t NSIZES = sizeof(SIZES) / sizeof(SIZES[0]);

// Repetitions per size
static const uint16_t REPS = 200;

// -----------------------------
// INPUTS / BUFFERS
// -----------------------------
static uint8_t KEY_16[16]   = {0};
static uint8_t NONCE_12[12] = {0};   // AES-GCM nonce
static uint8_t NONCE_16[16] = {0};   // ASCON nonce
static uint8_t AAD[16]      = {0};

static uint8_t PT[256];
static uint8_t CT[256];
static uint8_t TAG[16];

// ASCON output length
static unsigned long long clen = 0;

// -----------------------------
// TIMING HELPERS
// -----------------------------
static inline uint32_t now_us() { return micros(); }
// UNO @16MHz: rough cycles ≈ us * 16
static inline uint32_t us_to_cycles(uint32_t us) { return us * 16UL; }

// -----------------------------
// INIT
// -----------------------------
static void fill_inputs() {
  for (size_t i = 0; i < sizeof(PT); i++) PT[i] = (uint8_t)(i & 0xFF);
  for (size_t i = 0; i < sizeof(AAD); i++) AAD[i] = (uint8_t)(0xA0 + i);

  for (size_t i = 0; i < sizeof(KEY_16); i++) KEY_16[i] = (uint8_t)(0x10 + i);
  for (size_t i = 0; i < sizeof(NONCE_12); i++) NONCE_12[i] = (uint8_t)(0x20 + i);
  for (size_t i = 0; i < sizeof(NONCE_16); i++) NONCE_16[i] = (uint8_t)(0x30 + i);
}

// -----------------------------
// BENCHMARKS
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

static uint32_t bench_ascon(size_t mlen) {
  uint32_t t0 = now_us();

  for (uint16_t i = 0; i < REPS; i++) {
    clen = 0;
    crypto_aead_encrypt(
      CT, &clen,
      PT, (unsigned long long)mlen,
      AAD, (unsigned long long)sizeof(AAD),
      NULL,
      NONCE_16,
      KEY_16
    );
  }

  return now_us() - t0;
}

// -----------------------------
// ARDUINO ENTRYPOINT
// -----------------------------
void setup() {
  Serial.begin(BAUD);
  fill_inputs();
  delay(200);

  Serial.println(F("algo,msg_len,reps,total_us,avg_us,approx_cycles"));

  for (size_t si = 0; si < NSIZES; si++) {
    size_t mlen = SIZES[si];

    // AES-GCM
    uint32_t aes_us = bench_aes_gcm(mlen);
    float aes_avg = (float)aes_us / (float)REPS;

    Serial.print(F("AES-GCM,"));
    Serial.print(mlen); Serial.print(F(","));
    Serial.print(REPS); Serial.print(F(","));
    Serial.print(aes_us); Serial.print(F(","));
    Serial.print(aes_avg, 3); Serial.print(F(","));
    Serial.println(us_to_cycles((uint32_t)aes_avg));

    // ASCON
    uint32_t ascon_us = bench_ascon(mlen);
    float ascon_avg = (float)ascon_us / (float)REPS;

    Serial.print(F("ASCON,"));
    Serial.print(mlen); Serial.print(F(","));
    Serial.print(REPS); Serial.print(F(","));
    Serial.print(ascon_us); Serial.print(F(","));
    Serial.print(ascon_avg, 3); Serial.print(F(","));
    Serial.println(us_to_cycles((uint32_t)ascon_avg));
  }

  Serial.println(F("# Done"));
}

void loop() {}
