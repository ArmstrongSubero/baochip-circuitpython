// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "shared-bindings/microcontroller/Pin.h"
#include "common-hal/microcontroller/Pin.h"

#include "hardware/gpio.h"

// Six ports of 16 pins exist on the die; only PB and PC reach the Dabao.
#define PORT_COUNT  6

static uint16_t claimed_pins[PORT_COUNT];
static uint16_t never_reset_pins[PORT_COUNT];

// PC13 is the PROG strap and shorts USB when low. It only ever goes back
// to an input.
static bool is_usb_strap(uint8_t port, uint8_t pin) {
    return port == GPIO_PORT_C && pin == 13;
}

// With the REPL on UART2, PB13 and PB14 return to the UART when released.
static bool restore_console_pin(uint8_t port, uint8_t pin) {
    #if CIRCUITPY_PORT_SERIAL
    if (port != GPIO_PORT_B) {
        return false;
    }
    if (pin == 13) {
        gpio_set_function(port, pin, GPIO_FUNC_AF1);
        gpio_set_dir(port, pin, false);
        gpio_pull_up(port, pin);
        return true;
    }
    if (pin == 14) {
        gpio_set_function(port, pin, GPIO_FUNC_AF1);
        gpio_set_dir(port, pin, true);
        return true;
    }
    #else
    (void)port;
    (void)pin;
    #endif
    return false;
}

void reset_pin_number(uint8_t pin_number) {
    uint8_t port = pin_number / 16;
    uint8_t pin = pin_number % 16;
    if (port >= PORT_COUNT) {
        return;
    }
    if (never_reset_pins[port] & (1u << pin)) {
        return;
    }
    bool was_claimed = claimed_pins[port] & (1u << pin);
    claimed_pins[port] &= ~(1u << pin);
    if (!was_claimed) {
        return;
    }
    if (is_usb_strap(port, pin)) {
        gpio_set_dir(port, pin, false);
        gpio_disable_pulls(port, pin);
        return;
    }
    if (restore_console_pin(port, pin)) {
        return;
    }
    gpio_init(port, pin);
}

// Only claimed pins are reset.
void reset_all_pins(void) {
    for (uint8_t port = 0; port < PORT_COUNT; port++) {
        for (uint8_t pin = 0; pin < 16; pin++) {
            if (claimed_pins[port] & (1u << pin)) {
                reset_pin_number(port * 16 + pin);
            }
        }
    }
}

uint8_t common_hal_mcu_pin_number(const mcu_pin_obj_t *pin) {
    return pin->port * 16 + pin->number;
}

bool common_hal_mcu_pin_is_free(const mcu_pin_obj_t *pin) {
    return !(claimed_pins[pin->port] & (1u << pin->number));
}

void common_hal_reset_pin(const mcu_pin_obj_t *pin) {
    if (pin == NULL) {
        return;
    }
    reset_pin_number(common_hal_mcu_pin_number(pin));
}

void common_hal_never_reset_pin(const mcu_pin_obj_t *pin) {
    if (pin == NULL) {
        return;
    }
    never_reset_pins[pin->port] |= (1u << pin->number);
}

void claim_pin(const mcu_pin_obj_t *pin) {
    claimed_pins[pin->port] |= (1u << pin->number);
}

void common_hal_mcu_pin_claim(const mcu_pin_obj_t *pin) {
    claim_pin(pin);
}

void common_hal_mcu_pin_reset_number(uint8_t pin_no) {
    reset_pin_number(pin_no);
}
