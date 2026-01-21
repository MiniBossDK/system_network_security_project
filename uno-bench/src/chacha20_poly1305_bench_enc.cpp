/*
 * ChaCha20-Poly1305 Encryption Performance Test (CSV Output)
 * Library: rweather/arduinolibs
 * Hardware: Arduino Uno Rev3
 */
#include <avr/sleep.h>
#include <Arduino.h>
#include <Crypto.h>
#include <ChaChaPoly.h>

// Initialize ChaCha20-Poly1305
ChaChaPoly chachaPoly;

// --- Configuration ---
const size_t MAX_MESSAGE_SIZE = 512;
const size_t TAG_SIZE = 16;
const size_t IV_SIZE = 12;   // ChaChaPoly typically uses a 12-byte (96-bit) nonce
const size_t KEY_SIZE = 32;  // ChaCha20 uses a 32-byte (256-bit) Key

const int REPS = 10000; // 50

// Buffers
uint8_t buffer[MAX_MESSAGE_SIZE];
uint8_t tag[TAG_SIZE];
uint8_t iv[IV_SIZE] = {
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 
    0x18, 0x19, 0x1a, 0x1b
};
uint8_t key[KEY_SIZE] = {
    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 
    0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
    0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 
    0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20
};

// Message sizes to test
const size_t sizes[] = {512}; // 16, 32, 64, 128, 256, 512

void setup() {
    Serial.begin(115200);
    while (!Serial);

    Serial.println(F("### TRIGGER! ###"));

    // Set the key once
    chachaPoly.setKey(key, KEY_SIZE);

    //Serial.println(F("algo,msg_len,reps,total_us,avg_us,approx_cycles"));

    for (size_t i = 0; i < sizeof(sizes) / sizeof(sizes[0]); i++) {
        size_t msgSize = sizes[i];
        
        memset(buffer, 0x42, msgSize);

        //unsigned long start = micros();

        for (int r = 0; r < REPS; r++) {
            // 1. Set IV (Nonce)
            chachaPoly.setIV(iv, IV_SIZE);
            
            // 2. Encrypt in-place
            chachaPoly.encrypt(buffer, buffer, msgSize);
            
            // 3. Compute Tag
            chachaPoly.computeTag(tag, TAG_SIZE);
        }

        /* unsigned long total_us = micros() - start;

        float avg_us = (float)total_us / REPS;
        unsigned long approx_cycles = (unsigned long)(avg_us * 16.0);

        Serial.print(F("ChaChaPoly-ENC,"));
        Serial.print(msgSize);
        Serial.print(F(","));
        Serial.print(REPS);
        Serial.print(F(","));
        Serial.print(total_us);
        Serial.print(F(","));
        Serial.print(avg_us, 2);
        Serial.print(F(","));
        Serial.println(approx_cycles); */
    }
    Serial.println(F("# Done"));
}

void loop() {}