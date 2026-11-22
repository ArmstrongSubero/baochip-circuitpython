// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

// aesio on the chip's AES engine. Replaces shared-module/aesio and keeps
// its object layout, so the bindings are unchanged. The engine holds one
// key, so each object reloads its own key and IV on every call.

#include <string.h>

#include "py/runtime.h"
#include "shared-bindings/aesio/__init__.h"
#include "shared-module/aesio/__init__.h"

#include "common-hal/aesio/engine.h"

#define CTR_BLOCKS  16

static uint8_t *obj_key(aesio_aes_obj_t *self) {
    return (uint8_t *)&self->ctx;
}

static void check(int rc) {
    if (rc != 0) {
        mp_raise_RuntimeError(MP_ERROR_TEXT("AES engine failed"));
    }
}

static void load(aesio_aes_obj_t *self, bool with_iv) {
    check(baochip_aes_load(obj_key(self), self->ctx.KeyLength, with_iv ? self->ctx.Iv : NULL));
}

void common_hal_aesio_aes_construct(aesio_aes_obj_t *self, const uint8_t *key,
    uint32_t key_length, const uint8_t *iv, int mode, int counter) {
    self->mode = mode;
    self->counter = counter;
    common_hal_aesio_aes_rekey(self, key, key_length, iv);
}

void common_hal_aesio_aes_rekey(aesio_aes_obj_t *self, const uint8_t *key,
    uint32_t key_length, const uint8_t *iv) {
    memset(&self->ctx, 0, sizeof(self->ctx));
    memcpy(obj_key(self), key, key_length);
    self->ctx.KeyLength = key_length;
    if (iv != NULL) {
        memcpy(self->ctx.Iv, iv, AES_BLOCKLEN);
    }
}

void common_hal_aesio_aes_set_mode(aesio_aes_obj_t *self, int mode) {
    self->mode = mode;
}

static void counter_increment(uint8_t *counter) {
    for (int i = AES_BLOCKLEN - 1; i >= 0; i--) {
        if (++counter[i] != 0) {
            break;
        }
    }
}

// CTR runs the counter blocks through ECB. Each call starts on a fresh
// block, same as the software aesio.
static void ctr_xcrypt(aesio_aes_obj_t *self, uint8_t *buffer, size_t length) {
    uint8_t stream[CTR_BLOCKS * AES_BLOCKLEN];
    load(self, false);
    while (length > 0) {
        size_t take = length > sizeof(stream) ? sizeof(stream) : length;
        size_t blocks = (take + AES_BLOCKLEN - 1) / AES_BLOCKLEN;
        for (size_t b = 0; b < blocks; b++) {
            memcpy(&stream[b * AES_BLOCKLEN], self->ctx.Iv, AES_BLOCKLEN);
            counter_increment(self->ctx.Iv);
        }
        check(baochip_aes_ecb(true, stream, blocks * AES_BLOCKLEN));
        for (size_t i = 0; i < take; i++) {
            buffer[i] ^= stream[i];
        }
        buffer += take;
        length -= take;
    }
    memset(stream, 0, sizeof(stream));
}

void common_hal_aesio_aes_encrypt(aesio_aes_obj_t *self, uint8_t *buffer, size_t length) {
    switch (self->mode) {
        case AES_MODE_ECB:
            load(self, false);
            check(baochip_aes_ecb(true, buffer, AES_BLOCKLEN));
            break;
        case AES_MODE_CBC:
            if (length == 0) {
                break;
            }
            load(self, true);
            check(baochip_aes_cbc(true, buffer, length));
            memcpy(self->ctx.Iv, buffer + length - AES_BLOCKLEN, AES_BLOCKLEN);
            break;
        case AES_MODE_CTR:
            ctr_xcrypt(self, buffer, length);
            break;
    }
}

void common_hal_aesio_aes_decrypt(aesio_aes_obj_t *self, uint8_t *buffer, size_t length) {
    switch (self->mode) {
        case AES_MODE_ECB:
            load(self, false);
            check(baochip_aes_ecb(false, buffer, AES_BLOCKLEN));
            break;
        case AES_MODE_CBC: {
            if (length == 0) {
                break;
            }
            uint8_t next_iv[AES_BLOCKLEN];
            memcpy(next_iv, buffer + length - AES_BLOCKLEN, AES_BLOCKLEN);
            load(self, true);
            check(baochip_aes_cbc(false, buffer, length));
            memcpy(self->ctx.Iv, next_iv, AES_BLOCKLEN);
            break;
        }
        case AES_MODE_CTR:
            ctr_xcrypt(self, buffer, length);
            break;
    }
}
