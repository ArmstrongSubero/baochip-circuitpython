// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include <stdint.h>

#include "py/runtime.h"

#include "shared-bindings/pwmio/PWMOut.h"
#include "shared-bindings/microcontroller/Pin.h"

#include "bao.h"
#include "hardware/gpio.h"
#include "hardware/pwm.h"

// PWM1 is PB0 to PB3, PWM2 is PC0 to PC3. Channels of a slice share a
// counter, so they share a frequency.
#define PWM_CLOCK_HZ    (ACLK_HZ / 8)
#define SLICE_COUNT     4

typedef struct {
    uint8_t users;
    bool variable;
    uint32_t requested;
    uint32_t actual;
} slice_state_t;

static slice_state_t slices[SLICE_COUNT];

// Same search as pwm_init, to report the frequency it settles on.
static uint32_t actual_frequency(uint32_t freq_hz) {
    uint32_t prescaler;
    uint32_t period = 0;
    for (prescaler = 0; prescaler < 256; prescaler++) {
        period = (PWM_CLOCK_HZ / (prescaler + 1)) / freq_hz;
        if (period <= 65535) {
            break;
        }
    }
    if (prescaler > 255) {
        prescaler = 255;
        period = 65535;
    }
    if (period < 2) {
        period = 2;
    }
    return (PWM_CLOCK_HZ / (prescaler + 1)) / period;
}

static bool frequency_ok(uint32_t freq_hz) {
    return freq_hz >= 3 && freq_hz <= PWM_CLOCK_HZ / 2;
}

// Set to 1 for an SDK whose pwm_set_duty gives the inverse duty.
#ifndef BAOCHIP_PWM_HIGH_AFTER_MATCH
#define BAOCHIP_PWM_HIGH_AFTER_MATCH    0
#endif

static void apply_duty(pwmio_pwmout_obj_t *self) {
    uint32_t period = pwm_get_period(self->slice);
    uint32_t high = ((uint32_t)self->duty_cycle * period + 32767u) / 65535u;
    uint32_t compare = high;
    #if BAOCHIP_PWM_HIGH_AFTER_MATCH
    if (high > 0 && high < period) {
        compare = period - high;
    }
    #endif
    pwm_set_duty(self->slice, self->channel, (uint16_t)compare);
}

pwmout_result_t common_hal_pwmio_pwmout_construct(pwmio_pwmout_obj_t *self,
    const mcu_pin_obj_t *pin, uint16_t duty, uint32_t frequency,
    bool variable_frequency) {
    uint8_t slice;
    if (pin->port == GPIO_PORT_B && pin->number <= 3) {
        slice = 1;
    } else if (pin->port == GPIO_PORT_C && pin->number <= 3) {
        slice = 2;
    } else {
        return PWMOUT_INVALID_PIN;
    }
    if (!frequency_ok(frequency)) {
        return PWMOUT_INVALID_FREQUENCY;
    }

    slice_state_t *state = &slices[slice];
    if (state->users > 0) {
        if (variable_frequency || state->variable) {
            return PWMOUT_INTERNAL_RESOURCES_IN_USE;
        }
        if (state->requested != frequency) {
            return PWMOUT_INVALID_FREQUENCY;
        }
    } else {
        pwm_init(slice, frequency);
        state->requested = frequency;
        state->actual = actual_frequency(frequency);
        state->variable = variable_frequency;
    }
    state->users++;

    claim_pin(pin);
    self->pin = pin;
    self->slice = slice;
    self->channel = pin->number;
    self->variable_frequency = variable_frequency;
    self->duty_cycle = duty;

    apply_duty(self);
    pwm_init_pin(pin->port, pin->number);
    return PWMOUT_OK;
}

bool common_hal_pwmio_pwmout_deinited(pwmio_pwmout_obj_t *self) {
    return self->pin == NULL;
}

void common_hal_pwmio_pwmout_deinit(pwmio_pwmout_obj_t *self) {
    if (common_hal_pwmio_pwmout_deinited(self)) {
        return;
    }
    pwm_set_duty(self->slice, self->channel, 0);
    common_hal_reset_pin(self->pin);
    slice_state_t *state = &slices[self->slice];
    if (state->users > 0) {
        state->users--;
    }
    if (state->users == 0) {
        pwm_stop(self->slice);
        state->variable = false;
    }
    self->pin = NULL;
}

void baochip_pwmout_reset(void) {
    for (uint8_t slice = 0; slice < SLICE_COUNT; slice++) {
        if (slices[slice].users > 0) {
            pwm_stop(slice);
        }
        slices[slice].users = 0;
        slices[slice].variable = false;
    }
}

void common_hal_pwmio_pwmout_set_duty_cycle(pwmio_pwmout_obj_t *self, uint16_t duty) {
    self->duty_cycle = duty;
    apply_duty(self);
}

uint16_t common_hal_pwmio_pwmout_get_duty_cycle(pwmio_pwmout_obj_t *self) {
    return self->duty_cycle;
}

void common_hal_pwmio_pwmout_set_frequency(pwmio_pwmout_obj_t *self, uint32_t frequency) {
    if (!frequency_ok(frequency)) {
        mp_arg_error_invalid(MP_QSTR_frequency);
    }
    slice_state_t *state = &slices[self->slice];
    pwm_init(self->slice, frequency);
    state->requested = frequency;
    state->actual = actual_frequency(frequency);
    apply_duty(self);
}

uint32_t common_hal_pwmio_pwmout_get_frequency(pwmio_pwmout_obj_t *self) {
    return slices[self->slice].actual;
}

bool common_hal_pwmio_pwmout_get_variable_frequency(pwmio_pwmout_obj_t *self) {
    return self->variable_frequency;
}

const mcu_pin_obj_t *common_hal_pwmio_pwmout_get_pin(pwmio_pwmout_obj_t *self) {
    return self->pin;
}
