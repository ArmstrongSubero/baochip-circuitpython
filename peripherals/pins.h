// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#pragma once

#include <stdint.h>
#include "py/obj.h"

typedef struct {
    mp_obj_base_t base;
    uint8_t port;
    uint8_t number;
} mcu_pin_obj_t;

extern const mp_obj_type_t mcu_pin_type;

#define PIN(p, n) { { &mcu_pin_type }, .port = (p), .number = (n) }

extern const mcu_pin_obj_t pin_PB0;
extern const mcu_pin_obj_t pin_PB1;
extern const mcu_pin_obj_t pin_PB2;
extern const mcu_pin_obj_t pin_PB3;
extern const mcu_pin_obj_t pin_PB4;
extern const mcu_pin_obj_t pin_PB5;
extern const mcu_pin_obj_t pin_PB6;
extern const mcu_pin_obj_t pin_PB7;
extern const mcu_pin_obj_t pin_PB8;
extern const mcu_pin_obj_t pin_PB9;
extern const mcu_pin_obj_t pin_PB10;
extern const mcu_pin_obj_t pin_PB11;
extern const mcu_pin_obj_t pin_PB12;
extern const mcu_pin_obj_t pin_PB13;
extern const mcu_pin_obj_t pin_PB14;
extern const mcu_pin_obj_t pin_PB15;
extern const mcu_pin_obj_t pin_PC0;
extern const mcu_pin_obj_t pin_PC1;
extern const mcu_pin_obj_t pin_PC2;
extern const mcu_pin_obj_t pin_PC3;
extern const mcu_pin_obj_t pin_PC4;
extern const mcu_pin_obj_t pin_PC5;
extern const mcu_pin_obj_t pin_PC6;
extern const mcu_pin_obj_t pin_PC7;
extern const mcu_pin_obj_t pin_PC8;
extern const mcu_pin_obj_t pin_PC9;
extern const mcu_pin_obj_t pin_PC10;
extern const mcu_pin_obj_t pin_PC11;
extern const mcu_pin_obj_t pin_PC12;
extern const mcu_pin_obj_t pin_PC13;
extern const mcu_pin_obj_t pin_PC14;
extern const mcu_pin_obj_t pin_PC15;
