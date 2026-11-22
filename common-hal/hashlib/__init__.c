// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

// hashlib on the chip's hash engine.

#include <string.h>

#include "shared-bindings/hashlib/__init__.h"

bool common_hal_hashlib_new(hashlib_hash_obj_t *self, const char *algorithm) {
    if (strcmp(algorithm, "sha256") == 0) {
        self->digest_size = SHA256_DIGEST_SIZE;
        return sha256_stream_init((sha256_ctx_t *)&self->stream) == SHA_OK;
    }
    if (strcmp(algorithm, "sha512") == 0) {
        self->digest_size = SHA512_DIGEST_SIZE;
        return sha512_stream_init((sha512_ctx_t *)&self->stream) == SHA_OK;
    }
    return false;
}
