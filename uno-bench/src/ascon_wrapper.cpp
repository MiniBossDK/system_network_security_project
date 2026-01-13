#include <Arduino.h>
#include <Crypto.h>
#include <Ascon128.h>

// Link to the Ascon128 implementation in rweather/CryptoLW
// Ensure your platformio.ini or Arduino library manager has CryptoLW installed.

extern "C" int crypto_aead_encrypt(
  unsigned char *c, unsigned long long *clen,
  const unsigned char *m, unsigned long long mlen,
  const unsigned char *ad, unsigned long long adlen,
  const unsigned char *nsec,
  const unsigned char *npub,
  const unsigned char *k
) {
    Ascon128 cipher;

    // 1. Initialize Key and Nonce (IV)
    // Ascon128::setKey expects 16 bytes
    // Ascon128::setIV expects 16 bytes (NIST "npub" is the Nonce/IV)
    cipher.clear();
    cipher.setKey(k, 16);
    cipher.setIV(npub, 16);

    // 2. Process Associated Data (AAD)
    // Only if adlen > 0. The library handles buffering internally.
    if (adlen > 0) {
        cipher.addAuthData(ad, (size_t)adlen);
    }

    // 3. Encrypt Plaintext
    // Writes 'mlen' bytes of ciphertext into 'c'.
    // The library allows input 'm' and output 'c' to overlap/be the same buffer.
    cipher.encrypt(c, m, (size_t)mlen);

    // 4. Compute Authentication Tag
    // The NIST API expects the tag to be appended to the end of the ciphertext.
    // Ascon-128 standard tag size is 16 bytes.
    cipher.computeTag(c + mlen, 16);

    // 5. Set Output Length
    // Total length = Ciphertext length + Tag length
    *clen = mlen + 16;

    // Return 0 for success
    return 0;
}