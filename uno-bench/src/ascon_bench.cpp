#include <Arduino.h>
#include <Crypto.h>
#include <Ascon128.h>

// -----------------------------
// ASCON WRAPPER IMPLEMENTATION
// -----------------------------
int crypto_aead_encrypt(
  unsigned char *c, unsigned long long *clen,
  const unsigned char *m, unsigned long long mlen,
  const unsigned char *ad, unsigned long long adlen,
  const unsigned char *nsec,
  const unsigned char *npub,
  const unsigned char *k
) {
    Ascon128 cipher;

    cipher.clear();
    cipher.setKey(k, 16);
    cipher.setIV(npub, 16);

    if (adlen > 0) {
        cipher.addAuthData(ad, (size_t)adlen);
    }

    cipher.encrypt(c, m, (size_t)mlen);
    
    // NIST API expects tag appended to ciphertext
    cipher.computeTag(c + mlen, 16);

    *clen = mlen + 16;
    return 0;
}

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
static uint8_t NONCE_16[16] = {0}; // ASCON uses 16-byte Nonce
static uint8_t AAD[16]      = {0};

static uint8_t PT[256];
// CT must accommodate PT + Tag (16 bytes)
static uint8_t CT[256 + 16]; 

static unsigned long long clen = 0;

// -----------------------------
// HELPERS
// -----------------------------
static inline uint32_t now_us() { return micros(); }
static inline uint32_t us_to_cycles(uint32_t us) { return us * 16UL; }

static void fill_inputs() {
  for (size_t i = 0; i < sizeof(PT); i++) PT[i] = (uint8_t)(i & 0xFF);
  for (size_t i = 0; i < sizeof(AAD); i++) AAD[i] = (uint8_t)(0xA0 + i);
  for (size_t i = 0; i < sizeof(KEY_16); i++) KEY_16[i] = (uint8_t)(0x10 + i);
  for (size_t i = 0; i < sizeof(NONCE_16); i++) NONCE_16[i] = (uint8_t)(0x30 + i);
}

// -----------------------------
// BENCHMARK: ASCON
// -----------------------------
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
// ENTRYPOINT
// -----------------------------
void setup() {
  Serial.begin(BAUD);
  fill_inputs();
  delay(200);

  Serial.println(F("algo,msg_len,reps,total_us,avg_us,approx_cycles"));

  for (size_t si = 0; si < NSIZES; si++) {
    size_t mlen = SIZES[si];

    uint32_t total_us = bench_ascon(mlen);
    float avg_us = (float)total_us / (float)REPS;

    Serial.print(F("ASCON,"));
    Serial.print(mlen); Serial.print(F(","));
    Serial.print(REPS); Serial.print(F(","));
    Serial.print(total_us); Serial.print(F(","));
    Serial.print(avg_us, 3); Serial.print(F(","));
    Serial.println(us_to_cycles((uint32_t)avg_us));
  }

  Serial.println(F("# Done"));
}

void loop() {}