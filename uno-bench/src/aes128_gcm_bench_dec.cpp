/*
 * AES128-GCM Decryption Performance Test (CSV Output)
 * Library: rweather/arduinolibs
 * Hardware: Arduino Uno Rev3
 * * NOTE: This sketch uses dummy data as "ciphertext". 
 * The tag check will fail (return false), but the execution time 
 * is mathematically identical to valid decryption.
 */

#include <avr/sleep.h>
#include <Arduino.h>
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

// Repetitions for averaging
const int REPS = 10000; // 50 

// Buffers
uint8_t buffer[MAX_MESSAGE_SIZE]; // Holds the "Ciphertext"
uint8_t expectedTag[TAG_SIZE];    // Holds the expected auth tag
uint8_t iv[IV_SIZE] = {0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b};
uint8_t key[KEY_SIZE] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x00};

// Message sizes to test
const size_t sizes[] = {16}; // 16, 32, 64, 128, 256, 512

void setup() {
    Serial.begin(115200);
    while (!Serial);

    Serial.println(F("### TRIGGER! ###"));

    // Set the key once
    gcm.setKey(key, KEY_SIZE);

    // Prepare dummy "Pre-existing Ciphertext" and Tag
    // In a real scenario, this would be data received over the network
    memset(buffer, 0xAB, MAX_MESSAGE_SIZE); 
    memset(expectedTag, 0xCD, TAG_SIZE);
    
    // CSV Header
    //Serial.println(F("algo,msg_len,reps,total_us,avg_us,approx_cycles"));

    for (size_t i = 0; i < sizeof(sizes) / sizeof(sizes[0]); i++) {
        size_t msgSize = sizes[i];

        // --- Start Timing Block ---
        //unsigned long start = micros();

        for (int r = 0; r < REPS; r++) {
            // 1. Set IV (Required before every packet)
            gcm.setIV(iv, IV_SIZE);
            
            // 2. Decrypt (In-place: Ciphertext -> Plaintext)
            // Note: This performs the AES-CTR operations
            gcm.decrypt(buffer, buffer, msgSize);
            
            // 3. Check Tag (Verify integrity)
            // Note: This performs the GHASH multiplication
            // It will return false here because data is dummy, but time is accurate.
            volatile bool valid = gcm.checkTag(expectedTag, TAG_SIZE);
        }

        /* unsigned long total_us = micros() - start;
        // --- End Timing Block ---

        // Calculations
        float avg_us = (float)total_us / REPS;
        unsigned long approx_cycles = (unsigned long)(avg_us * 16.0);

        // Print CSV Row
        Serial.print(F("AES128-GCM-DEC,"));
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

void loop() {
    // Run once
}