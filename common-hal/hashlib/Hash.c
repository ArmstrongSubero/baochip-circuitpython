// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include <string.h>

#include "py/runtime.h"
#include "shared-bindings/hashlib/Hash.h"

void common_hal_hashlib_hash_update(hashlib_hash_obj_t *self, const uint8_t *data, size_t datalen) {
    if (datalen == 0) {
        return;
    }
    int rc;
    if (self->digest_size == SHA256_DIGEST_SIZE) {
        rc = sha256_stream_update((sha256_ctx_t *)&self->stream, data, datalen);
    } else {
        rc = sha512_stream_update((sha512_ctx_t *)&self->stream, data, datalen);
    }
    if (rc != SHA_OK) {
        mp_raise_RuntimeError(MP_ERROR_TEXT("Hash engine failed"));
    }
}

// Finish on a copy so update() still works after digest().
void common_hal_hashlib_hash_digest(hashlib_hash_obj_t *self, uint8_t *data, size_t datalen) {
    if (datalen < self->digest_size) {
        return;
    }
    sha2_stream_t copy;
    memcpy(&copy, &self->stream, sizeof(copy));
    int rc;
    if (self->digest_size == SHA256_DIGEST_SIZE) {
        rc = sha256_stream_final((sha256_ctx_t *)&copy, data);
    } else {
        rc = sha512_stream_final((sha512_ctx_t *)&copy, data);
    }
    memset(&copy, 0, sizeof(copy));
    if (rc != SHA_OK) {
        mp_raise_RuntimeError(MP_ERROR_TEXT("Hash engine failed"));
    }
}

size_t common_hal_hashlib_hash_get_digest_size(hashlib_hash_obj_t *self) {
    return self->digest_size;
}
