// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/mpconfig.h"
#include "py/obj.h"

#include "shared-bindings/os/__init__.h"

#include "hardware/trng.h"

static bool trng_ready = false;

bool common_hal_os_urandom(uint8_t *buffer, mp_uint_t length) {
    if (!trng_ready) {
        trng_init();
        trng_ready = true;
    }
    while (length > 0) {
        uint32_t word;
        if (trng_generate(&word, 1) != 0) {
            return false;
        }
        for (int i = 0; i < 4 && length > 0; i++) {
            *buffer++ = (uint8_t)(word >> (8 * i));
            length--;
        }
    }
    return true;
}
