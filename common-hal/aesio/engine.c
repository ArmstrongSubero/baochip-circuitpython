// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "common-hal/aesio/engine.h"

#include "hardware/aes.h"

int baochip_aes_load(const uint8_t *key, uint32_t key_length, const uint8_t *iv) {
    int rc = aes_set_key(key, key_length);
    if (rc == 0 && iv != NULL) {
        rc = aes_set_iv(iv);
    }
    return rc;
}

int baochip_aes_ecb(bool encrypt, uint8_t *buffer, size_t length) {
    if (encrypt) {
        return aes_encrypt_mode(AES_MODE_ECB, buffer, buffer, length);
    }
    return aes_decrypt_mode(AES_MODE_ECB, buffer, buffer, length);
}

int baochip_aes_cbc(bool encrypt, uint8_t *buffer, size_t length) {
    if (encrypt) {
        return aes_encrypt_mode(AES_MODE_CBC, buffer, buffer, length);
    }
    return aes_decrypt_mode(AES_MODE_CBC, buffer, buffer, length);
}
