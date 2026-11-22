// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#pragma once

#include "py/mphal.h"
#include "peripherals/pins.h"

void reset_all_pins(void);
void reset_pin_number(uint8_t pin_number);
void claim_pin(const mcu_pin_obj_t *pin);
void common_hal_reset_pin(const mcu_pin_obj_t *pin);
void common_hal_never_reset_pin(const mcu_pin_obj_t *pin);
uint8_t common_hal_mcu_pin_number(const mcu_pin_obj_t *pin);
void common_hal_mcu_pin_claim(const mcu_pin_obj_t *pin);
