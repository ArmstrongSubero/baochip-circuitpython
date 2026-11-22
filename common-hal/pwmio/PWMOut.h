// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#pragma once

#include "common-hal/microcontroller/Pin.h"
#include "py/obj.h"

typedef struct {
    mp_obj_base_t base;
    const mcu_pin_obj_t *pin;
    uint8_t slice;
    uint8_t channel;
    bool variable_frequency;
    uint16_t duty_cycle;
} pwmio_pwmout_obj_t;

void baochip_pwmout_reset(void);
