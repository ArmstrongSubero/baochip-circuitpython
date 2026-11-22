// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/obj.h"
#include "py/runtime.h"

#include "hardware/sha.h"

//| """Baochip-1x security engine
//|
//| Functions that run on the chip's own crypto hardware and have no
//| standard CircuitPython module. SHA-256 and SHA-512 are in `hashlib` and
//| AES is in `aesio`, both on the same hardware."""
//|

static mp_obj_t hmac_common(mp_obj_t key_in, mp_obj_t msg_in, size_t size) {
    mp_buffer_info_t key, msg;
    mp_get_buffer_raise(key_in, &key, MP_BUFFER_READ);
    mp_get_buffer_raise(msg_in, &msg, MP_BUFFER_READ);
    uint8_t mac[SHA512_DIGEST_SIZE];
    int rc;
    if (size == SHA256_DIGEST_SIZE) {
        rc = hmac_sha256(key.buf, key.len, msg.buf, msg.len, mac);
    } else {
        rc = hmac_sha512(key.buf, key.len, msg.buf, msg.len, mac);
    }
    if (rc != SHA_OK) {
        mp_raise_RuntimeError(MP_ERROR_TEXT("Hash engine failed"));
    }
    return mp_obj_new_bytes(mac, size);
}

//| def hmac_sha256(key: ReadableBuffer, msg: ReadableBuffer) -> bytes:
//|     """HMAC of ``msg`` under ``key`` with SHA-256. Returns 32 bytes."""
//|     ...
//|
static mp_obj_t baosec_hmac_sha256(mp_obj_t key_in, mp_obj_t msg_in) {
    return hmac_common(key_in, msg_in, SHA256_DIGEST_SIZE);
}
static MP_DEFINE_CONST_FUN_OBJ_2(baosec_hmac_sha256_obj, baosec_hmac_sha256);

//| def hmac_sha512(key: ReadableBuffer, msg: ReadableBuffer) -> bytes:
//|     """HMAC of ``msg`` under ``key`` with SHA-512. Returns 64 bytes."""
//|     ...
//|
static mp_obj_t baosec_hmac_sha512(mp_obj_t key_in, mp_obj_t msg_in) {
    return hmac_common(key_in, msg_in, SHA512_DIGEST_SIZE);
}
static MP_DEFINE_CONST_FUN_OBJ_2(baosec_hmac_sha512_obj, baosec_hmac_sha512);

//| def compare(a: ReadableBuffer, b: ReadableBuffer) -> bool:
//|     """True if ``a`` and ``b`` hold the same bytes. Takes the same time
//|     wherever they differ, for checking a MAC."""
//|     ...
//|
static mp_obj_t baosec_compare(mp_obj_t a_in, mp_obj_t b_in) {
    mp_buffer_info_t a, b;
    mp_get_buffer_raise(a_in, &a, MP_BUFFER_READ);
    mp_get_buffer_raise(b_in, &b, MP_BUFFER_READ);
    if (a.len != b.len) {
        return mp_const_false;
    }
    uint8_t diff = 0;
    for (size_t i = 0; i < a.len; i++) {
        diff |= ((const uint8_t *)a.buf)[i] ^ ((const uint8_t *)b.buf)[i];
    }
    return mp_obj_new_bool(diff == 0);
}
static MP_DEFINE_CONST_FUN_OBJ_2(baosec_compare_obj, baosec_compare);

static const mp_rom_map_elem_t baosec_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_baosec) },
    { MP_ROM_QSTR(MP_QSTR_hmac_sha256), MP_ROM_PTR(&baosec_hmac_sha256_obj) },
    { MP_ROM_QSTR(MP_QSTR_hmac_sha512), MP_ROM_PTR(&baosec_hmac_sha512_obj) },
    { MP_ROM_QSTR(MP_QSTR_compare), MP_ROM_PTR(&baosec_compare_obj) },
};
static MP_DEFINE_CONST_DICT(baosec_module_globals, baosec_module_globals_table);

const mp_obj_module_t baosec_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&baosec_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_baosec, baosec_module);
