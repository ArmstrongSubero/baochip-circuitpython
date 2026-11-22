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
    const mcu_pin_obj_t *clock;
    const mcu_pin_obj_t *mosi;
    const mcu_pin_obj_t *miso;
    uint32_t frequency;
    uint8_t clkdiv;
    uint8_t polarity;
    uint8_t phase;
    bool has_lock;
} busio_spi_obj_t;
