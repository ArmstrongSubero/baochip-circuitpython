// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/runtime.h"

#include "shared-bindings/analogio/AnalogOut.h"

// The Baochip-1x has no DAC.

void common_hal_analogio_analogout_construct(analogio_analogout_obj_t *self,
    const mcu_pin_obj_t *pin) {
    mp_raise_NotImplementedError_varg(MP_ERROR_TEXT("%q"), MP_QSTR_AnalogOut);
}

bool common_hal_analogio_analogout_deinited(analogio_analogout_obj_t *self) {
    return true;
}

void common_hal_analogio_analogout_deinit(analogio_analogout_obj_t *self) {
}

void common_hal_analogio_analogout_set_value(analogio_analogout_obj_t *self,
    uint16_t value) {
}
