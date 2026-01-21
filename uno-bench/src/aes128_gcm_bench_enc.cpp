/*
 * AES128-GCM Performance Test (CSV Output)
 * Library: rweather/arduinolibs
 * Hardware: Arduino Uno Rev3 (16 MHz)
 */
#include <Arduino.h>
#include <avr/sleep.h>
#include <Crypto.h>
#include <AES.h>
#include <GCM.h>


// Initialize GCM with AES128
GCM<AES128> gcm;

// --- Configuration ---
const size_t MAX_MESSAGE_SIZE = 512;
const size_t TAG_SIZE = 16;
const size_t IV_SIZE = 12;
const size_t KEY_SIZE = 16;

// Number of repetitions per message size to calculate average
const int REPS = 10000;

// Buffers
uint8_t buffer[MAX_MESSAGE_SIZE];
uint8_t tag[TAG_SIZE];
uint8_t iv[IV_SIZE] = {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b};
uint8_t key[KEY_SIZE] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x00};

// Message sizes to test
const size_t sizes[] = {512}; // 16, 32, 64, 128, 256, 512

void setup() {
    Serial.begin(115200);
    while (!Serial);

    Serial.println(F("### TRIGGER! ###"));

    // Set the key once
    gcm.setKey(key, KEY_SIZE);

    // CSV Header
    //Serial.println(F("algo,msg_len,reps,total_us,avg_us,approx_cycles"));

    // Iterate through sizes
    for (size_t i = 0; i < sizeof(sizes) / sizeof(sizes[0]); i++) {
        size_t msgSize = sizes[i];
        
        // Prepare dummy data
        memset(buffer, 0x42, msgSize);

        // --- Start Timing Block ---
        //unsigned long start = micros();

        for (int r = 0; r < REPS; r++) {
            // 1. Reset IV for each packet
            gcm.setIV(iv, IV_SIZE);
            
            // 2. Encrypt in-place
            gcm.encrypt(buffer, buffer, msgSize);
            
            // 3. Compute Tag
            gcm.computeTag(tag, TAG_SIZE);
        }
        
        /* unsigned long total_us = micros() - start;
        // --- End Timing Block ---

        // Calculations
        float avg_us = (float)total_us / REPS;
        
        // Arduino Uno runs at 16 MHz (1 us = 16 cycles)
        unsigned long approx_cycles = (unsigned long)(avg_us * 16.0);

        // Print CSV Row
        Serial.print(F("AES128-GCM-ENC,"));
        Serial.print(msgSize);
        Serial.print(F(","));
        Serial.print(REPS);
        Serial.print(F(","));
        Serial.print(total_us);
        Serial.print(F(","));
        Serial.print(avg_us, 2); // Print with 2 decimal places
        Serial.print(F(","));
        Serial.println(approx_cycles);   */ 
    }
    Serial.println(F("# Done"));
}

void loop() {
    // Run once
}