// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/mperrno.h"
#include "py/mphal.h"
#include "py/runtime.h"

#include "shared-bindings/busio/I2C.h"
#include "shared-bindings/microcontroller/Pin.h"

#include "hardware/gpio.h"
#include "hardware/i2c.h"

// I2C0: SCL on PB11, SDA on PB12.
#define I2C_INSTANCE    0

static bool i2c_in_use;

void common_hal_busio_i2c_construct(busio_i2c_obj_t *self,
    const mcu_pin_obj_t *scl, const mcu_pin_obj_t *sda,
    uint32_t frequency, uint32_t timeout_ms) {
    (void)timeout_ms;

    if (scl != &pin_PB11 || sda != &pin_PB12) {
        raise_ValueError_invalid_pins();
    }
    if (i2c_in_use) {
        mp_raise_ValueError(MP_ERROR_TEXT("I2C peripheral in use"));
    }
    mp_arg_validate_int_range(frequency, 1000, 1000000, MP_QSTR_frequency);

    claim_pin(scl);
    claim_pin(sda);
    self->scl = scl;
    self->sda = sda;
    self->frequency = frequency;
    self->has_lock = false;
    i2c_in_use = true;

    i2c_init(I2C_INSTANCE, frequency);
}

bool common_hal_busio_i2c_deinited(busio_i2c_obj_t *self) {
    return self->sda == NULL;
}

void common_hal_busio_i2c_mark_deinit(busio_i2c_obj_t *self) {
    self->sda = NULL;
}

void common_hal_busio_i2c_deinit(busio_i2c_obj_t *self) {
    if (common_hal_busio_i2c_deinited(self)) {
        return;
    }
    common_hal_reset_pin(self->scl);
    common_hal_reset_pin(self->sda);
    self->scl = NULL;
    i2c_in_use = false;
    common_hal_busio_i2c_mark_deinit(self);
}

void baochip_i2c_reset(void) {
    i2c_in_use = false;
}

static mp_negative_errno_t i2c_result(int status) {
    switch (status) {
        case I2C_OK:
            return 0;
        case I2C_ERR_NACK:
            return -MP_ENODEV;
        case I2C_ERR_TIMEOUT:
            return -MP_ETIMEDOUT;
        case I2C_ERR_LEN:
            return -MP_EINVAL;
        default:
            return -MP_EIO;
    }
}

bool common_hal_busio_i2c_probe(busio_i2c_obj_t *self, uint8_t addr) {
    uint8_t none = 0;
    return i2c_write_blocking(I2C_INSTANCE, addr, &none, 0) == I2C_OK;
}

bool common_hal_busio_i2c_try_lock(busio_i2c_obj_t *self) {
    if (common_hal_busio_i2c_deinited(self)) {
        return false;
    }
    bool grabbed_lock = false;
    if (!self->has_lock) {
        grabbed_lock = true;
        self->has_lock = true;
    }
    return grabbed_lock;
}

bool common_hal_busio_i2c_has_lock(busio_i2c_obj_t *self) {
    return self->has_lock;
}

void common_hal_busio_i2c_unlock(busio_i2c_obj_t *self) {
    self->has_lock = false;
}

mp_negative_errno_t common_hal_busio_i2c_write(busio_i2c_obj_t *self, uint16_t addr,
    const uint8_t *data, size_t len) {
    uint8_t none = 0;
    if (data == NULL || len == 0) {
        data = &none;
        len = 0;
    }
    return i2c_result(i2c_write_blocking(I2C_INSTANCE, addr, data, len));
}

mp_negative_errno_t common_hal_busio_i2c_read(busio_i2c_obj_t *self, uint16_t addr,
    uint8_t *data, size_t len) {
    return i2c_result(i2c_read_blocking(I2C_INSTANCE, addr, data, len));
}

mp_negative_errno_t common_hal_busio_i2c_write_read(busio_i2c_obj_t *self, uint16_t addr,
    uint8_t *out_data, size_t out_len, uint8_t *in_data, size_t in_len) {
    return i2c_result(i2c_write_read_blocking(I2C_INSTANCE, addr,
        out_data, out_len, in_data, in_len));
}
