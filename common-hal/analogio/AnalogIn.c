// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/runtime.h"

#include "shared-bindings/analogio/AnalogIn.h"
#include "shared-bindings/microcontroller/Pin.h"

#include "hardware/adc.h"
#include "hardware/gpio.h"

// ADC0 on PC9. 10 bits against the 1.208 V bandgap, accurate from 0.3 V
// to 1.0 V.

void common_hal_analogio_analogin_construct(analogio_analogin_obj_t *self,
    const mcu_pin_obj_t *pin) {
    if (pin != &pin_PC9) {
        raise_ValueError_invalid_pin();
    }
    claim_pin(pin);
    self->pin = pin;
    self->channel = 0;
    adc_init();
}

bool common_hal_analogio_analogin_deinited(analogio_analogin_obj_t *self) {
    return self->pin == NULL;
}

void common_hal_analogio_analogin_deinit(analogio_analogin_obj_t *self) {
    if (common_hal_analogio_analogin_deinited(self)) {
        return;
    }
    common_hal_reset_pin(self->pin);
    self->pin = NULL;
}

uint16_t common_hal_analogio_analogin_get_value(analogio_analogin_obj_t *self) {
    uint32_t raw = adc_read_raw(self->channel) & ADC_MAX_VALUE;
    return (uint16_t)((raw << 6) | (raw >> 4));
}

float common_hal_analogio_analogin_get_reference_voltage(analogio_analogin_obj_t *self) {
    return ADC_VREF_MV / 1000.0f;
}
