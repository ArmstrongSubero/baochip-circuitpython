// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include <string.h>

#include "py/mperrno.h"
#include "py/runtime.h"

#include "shared-bindings/busio/SPI.h"
#include "shared-bindings/microcontroller/Pin.h"
#include "supervisor/shared/translate/translate.h"

#include "hardware/gpio.h"
#include "hardware/spi.h"
#include "hardware/uart.h"

// SPI2: SCK on PC0, MOSI on PC1, MISO on PC2. Chip select is any GPIO.
#define SPI_INSTANCE    2
#define SPI_CHUNK       256

static bool spi_in_use;

// Clock is perclk / (2 * (clkdiv + 1)), and clkdiv is 8 bits.
static uint8_t clkdiv_for(uint32_t baudrate, uint32_t *actual) {
    uint32_t perclk = uart_get_perclk();
    uint32_t div = (perclk + 2 * baudrate - 1) / (2 * baudrate);
    if (div < 1) {
        div = 1;
    }
    if (div > 256) {
        div = 256;
    }
    *actual = perclk / (2 * div);
    return (uint8_t)(div - 1);
}

void common_hal_busio_spi_construct(busio_spi_obj_t *self,
    const mcu_pin_obj_t *clock, const mcu_pin_obj_t *mosi,
    const mcu_pin_obj_t *miso, bool half_duplex) {
    if (half_duplex) {
        mp_raise_NotImplementedError_varg(MP_ERROR_TEXT("%q"), MP_QSTR_half_duplex);
    }
    if (clock != &pin_PC0 || (mosi != NULL && mosi != &pin_PC1) ||
        (miso != NULL && miso != &pin_PC2) || (mosi == NULL && miso == NULL)) {
        raise_ValueError_invalid_pins();
    }
    if (spi_in_use) {
        mp_raise_ValueError(MP_ERROR_TEXT("SPI peripheral in use"));
    }

    claim_pin(clock);
    if (mosi != NULL) {
        claim_pin(mosi);
    }
    if (miso != NULL) {
        claim_pin(miso);
    }
    self->clock = clock;
    self->mosi = mosi;
    self->miso = miso;
    self->has_lock = false;
    spi_in_use = true;

    spi_init(SPI_INSTANCE);
    // spi_init takes all three pins. Hand back the one not asked for.
    if (mosi == NULL) {
        gpio_init(GPIO_PORT_C, 1);
    }
    if (miso == NULL) {
        gpio_init(GPIO_PORT_C, 2);
    }

    common_hal_busio_spi_configure(self, 250000, 0, 0, 8);
}

bool common_hal_busio_spi_deinited(busio_spi_obj_t *self) {
    return self->clock == NULL;
}

void common_hal_busio_spi_mark_deinit(busio_spi_obj_t *self) {
    self->clock = NULL;
}

void common_hal_busio_spi_deinit(busio_spi_obj_t *self) {
    if (common_hal_busio_spi_deinited(self)) {
        return;
    }
    common_hal_reset_pin(self->clock);
    common_hal_reset_pin(self->mosi);
    common_hal_reset_pin(self->miso);
    spi_in_use = false;
    common_hal_busio_spi_mark_deinit(self);
}

void baochip_spi_reset(void) {
    spi_in_use = false;
}

bool common_hal_busio_spi_configure(busio_spi_obj_t *self,
    uint32_t baudrate, uint8_t polarity, uint8_t phase, uint8_t bits) {
    if (bits != 8 || baudrate == 0) {
        return false;
    }
    self->clkdiv = clkdiv_for(baudrate, &self->frequency);
    self->polarity = polarity;
    self->phase = phase;
    spi_set_mode(SPI_INSTANCE, polarity, phase);
    return true;
}

bool common_hal_busio_spi_try_lock(busio_spi_obj_t *self) {
    if (common_hal_busio_spi_deinited(self)) {
        return false;
    }
    bool grabbed_lock = false;
    if (!self->has_lock) {
        grabbed_lock = true;
        self->has_lock = true;
    }
    return grabbed_lock;
}

bool common_hal_busio_spi_has_lock(busio_spi_obj_t *self) {
    return self->has_lock;
}

void common_hal_busio_spi_unlock(busio_spi_obj_t *self) {
    self->has_lock = false;
}

bool common_hal_busio_spi_write(busio_spi_obj_t *self,
    const uint8_t *data, size_t len) {
    if (self->mosi == NULL) {
        mp_raise_ValueError_varg(MP_ERROR_TEXT("No %q pin"), MP_QSTR_mosi);
    }
    while (len > 0) {
        size_t n = len > SPI_CHUNK ? SPI_CHUNK : len;
        spi_write_blocking(SPI_INSTANCE, data, n, self->clkdiv);
        data += n;
        len -= n;
    }
    return true;
}

bool common_hal_busio_spi_read(busio_spi_obj_t *self,
    uint8_t *data, size_t len, uint8_t write_value) {
    if (self->miso == NULL) {
        mp_raise_ValueError_varg(MP_ERROR_TEXT("No %q pin"), MP_QSTR_miso);
    }
    uint8_t fill[SPI_CHUNK];
    memset(fill, write_value, len > SPI_CHUNK ? SPI_CHUNK : len);
    while (len > 0) {
        size_t n = len > SPI_CHUNK ? SPI_CHUNK : len;
        spi_write_read_blocking(SPI_INSTANCE, fill, data, n, self->clkdiv);
        data += n;
        len -= n;
    }
    return true;
}

bool common_hal_busio_spi_transfer(busio_spi_obj_t *self,
    const uint8_t *data_out, uint8_t *data_in, size_t len) {
    if (self->mosi == NULL) {
        mp_raise_ValueError_varg(MP_ERROR_TEXT("No %q pin"), MP_QSTR_mosi);
    }
    if (self->miso == NULL) {
        mp_raise_ValueError_varg(MP_ERROR_TEXT("No %q pin"), MP_QSTR_miso);
    }
    while (len > 0) {
        size_t n = len > SPI_CHUNK ? SPI_CHUNK : len;
        spi_write_read_blocking(SPI_INSTANCE, data_out, data_in, n, self->clkdiv);
        data_out += n;
        data_in += n;
        len -= n;
    }
    return true;
}

uint32_t common_hal_busio_spi_get_frequency(busio_spi_obj_t *self) {
    return self->frequency;
}

uint8_t common_hal_busio_spi_get_phase(busio_spi_obj_t *self) {
    return self->phase;
}

uint8_t common_hal_busio_spi_get_polarity(busio_spi_obj_t *self) {
    return self->polarity;
}
