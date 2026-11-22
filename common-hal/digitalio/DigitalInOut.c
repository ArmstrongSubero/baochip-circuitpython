// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include <stdint.h>

#include "py/runtime.h"
#include "py/mphal.h"

#include "common-hal/microcontroller/Pin.h"
#include "shared-bindings/microcontroller/Pin.h"
#include "shared-bindings/digitalio/DigitalInOut.h"

#include "hardware/gpio.h"
#include "hardware/regs/addressmap.h"
#include "hardware/regs/iox.h"

// PC13 low shorts the USB data lines, so it is never driven.
static bool pin_is_input_only(const mcu_pin_obj_t *pin) {
    #if CIRCUITPY_USB_DEVICE
    return pin->port == GPIO_PORT_C && pin->number == 13;
    #else
    (void)pin;
    return false;
    #endif
}

digitalinout_result_t common_hal_digitalio_digitalinout_construct(
    digitalio_digitalinout_obj_t *self, const mcu_pin_obj_t *pin) {
    claim_pin(pin);
    self->pin = pin;
    self->output = false;
    self->open_drain = false;

    if (pin_is_input_only(pin)) {
        gpio_set_dir(pin->port, pin->number, false);
        gpio_disable_pulls(pin->port, pin->number);
    } else {
        gpio_init(pin->port, pin->number);
    }
    return DIGITALINOUT_OK;
}

bool common_hal_digitalio_digitalinout_deinited(digitalio_digitalinout_obj_t *self) {
    return self->pin == NULL;
}

void common_hal_digitalio_digitalinout_deinit(digitalio_digitalinout_obj_t *self) {
    if (common_hal_digitalio_digitalinout_deinited(self)) {
        return;
    }
    common_hal_reset_pin(self->pin);
    self->pin = NULL;
}

digitalinout_result_t common_hal_digitalio_digitalinout_switch_to_input(
    digitalio_digitalinout_obj_t *self, digitalio_pull_t pull) {
    return common_hal_digitalio_digitalinout_set_pull(self, pull);
}

digitalinout_result_t common_hal_digitalio_digitalinout_switch_to_output(
    digitalio_digitalinout_obj_t *self, bool value,
    digitalio_drive_mode_t drive_mode) {
    if (pin_is_input_only(self->pin)) {
        return DIGITALINOUT_INPUT_ONLY;
    }
    gpio_disable_pulls(self->pin->port, self->pin->number);
    self->output = true;
    self->open_drain = drive_mode == DRIVE_MODE_OPEN_DRAIN;
    common_hal_digitalio_digitalinout_set_value(self, value);
    return DIGITALINOUT_OK;
}

digitalio_direction_t common_hal_digitalio_digitalinout_get_direction(
    digitalio_digitalinout_obj_t *self) {
    return self->output ? DIRECTION_OUTPUT : DIRECTION_INPUT;
}

void common_hal_digitalio_digitalinout_set_value(
    digitalio_digitalinout_obj_t *self, bool value) {
    const uint8_t port = self->pin->port;
    const uint8_t pin = self->pin->number;
    if (self->open_drain && value) {
        gpio_set_dir(port, pin, false);
        gpio_put(port, pin, true);
    } else {
        gpio_put(port, pin, value);
        gpio_set_dir(port, pin, true);
    }
}

bool common_hal_digitalio_digitalinout_get_value(
    digitalio_digitalinout_obj_t *self) {
    return gpio_get(self->pin->port, self->pin->number);
}

digitalinout_result_t common_hal_digitalio_digitalinout_set_drive_mode(
    digitalio_digitalinout_obj_t *self,
    digitalio_drive_mode_t drive_mode) {
    bool value = common_hal_digitalio_digitalinout_get_value(self);
    self->open_drain = drive_mode == DRIVE_MODE_OPEN_DRAIN;
    if (value) {
        common_hal_digitalio_digitalinout_set_value(self, value);
    }
    return DIGITALINOUT_OK;
}

digitalio_drive_mode_t common_hal_digitalio_digitalinout_get_drive_mode(
    digitalio_digitalinout_obj_t *self) {
    return self->open_drain ? DRIVE_MODE_OPEN_DRAIN : DRIVE_MODE_PUSH_PULL;
}

// Pull ups only.
digitalinout_result_t common_hal_digitalio_digitalinout_set_pull(
    digitalio_digitalinout_obj_t *self, digitalio_pull_t pull) {
    if (pull == PULL_DOWN) {
        return DIGITALINOUT_INVALID_PULL;
    }
    const uint8_t port = self->pin->port;
    const uint8_t pin = self->pin->number;
    gpio_set_dir(port, pin, false);
    if (pull == PULL_UP) {
        gpio_pull_up(port, pin);
    } else {
        gpio_disable_pulls(port, pin);
    }
    self->output = false;
    return DIGITALINOUT_OK;
}

digitalio_pull_t common_hal_digitalio_digitalinout_get_pull(
    digitalio_digitalinout_obj_t *self) {
    if (self->output) {
        mp_raise_AttributeError(MP_ERROR_TEXT("Cannot get pull while in output mode"));
        return PULL_NONE;
    }
    return gpio_get_pull(self->pin->port, self->pin->number) ? PULL_UP : PULL_NONE;
}

bool common_hal_digitalio_has_reg_op(digitalinout_reg_op_t op) {
    return op == DIGITALINOUT_REG_READ || op == DIGITALINOUT_REG_WRITE;
}

volatile uint32_t *common_hal_digitalio_digitalinout_get_reg(
    digitalio_digitalinout_obj_t *self, digitalinout_reg_op_t op, uint32_t *mask) {
    *mask = 1u << self->pin->number;
    switch (op) {
        case DIGITALINOUT_REG_READ:
            return (volatile uint32_t *)(IOX_BASE + IOX_GPIOIN_PA_OFFSET + self->pin->port * 4);
        case DIGITALINOUT_REG_WRITE:
            return (volatile uint32_t *)(IOX_BASE + IOX_GPIOOUT_PA_OFFSET + self->pin->port * 4);
        default:
            return NULL;
    }
}
