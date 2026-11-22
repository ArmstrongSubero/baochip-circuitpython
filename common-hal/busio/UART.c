// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/mperrno.h"
#include "py/mphal.h"
#include "py/runtime.h"
#include "py/stream.h"
#include "shared/runtime/interrupt_char.h"

#include "shared-bindings/busio/UART.h"
#include "shared-bindings/microcontroller/Pin.h"
#include "supervisor/shared/tick.h"

#include "peripherals/console_uart.h"

// UART2: TX on PB14, RX on PB13.

void common_hal_busio_uart_construct(busio_uart_obj_t *self,
    const mcu_pin_obj_t *tx, const mcu_pin_obj_t *rx,
    const mcu_pin_obj_t *rts, const mcu_pin_obj_t *cts,
    const mcu_pin_obj_t *rs485_dir, bool rs485_invert,
    uint32_t baudrate, uint8_t bits, busio_uart_parity_t parity, uint8_t stop,
    mp_float_t timeout, uint16_t receiver_buffer_size, byte *receiver_buffer,
    bool sigint_enabled) {
    (void)rs485_invert;
    (void)receiver_buffer_size;
    (void)receiver_buffer;

    if ((tx != NULL && tx != &pin_PB14) || (rx != NULL && rx != &pin_PB13) ||
        (tx == NULL && rx == NULL)) {
        raise_ValueError_invalid_pins();
    }
    if (rts != NULL || cts != NULL || rs485_dir != NULL) {
        mp_raise_NotImplementedError(MP_ERROR_TEXT("RS485"));
    }
    if (bits != 8) {
        mp_arg_error_invalid(MP_QSTR_bits);
    }
    if (parity != BUSIO_UART_PARITY_NONE) {
        mp_arg_error_invalid(MP_QSTR_parity);
    }
    if (stop != 1) {
        mp_arg_error_invalid(MP_QSTR_stop);
    }
    if (baochip_uart2_claimed()) {
        mp_raise_ValueError(MP_ERROR_TEXT("UART peripheral in use"));
    }

    if (tx != NULL) {
        claim_pin(tx);
    }
    if (rx != NULL) {
        claim_pin(rx);
    }
    self->tx = tx;
    self->rx = rx;
    self->timeout_ms = (uint32_t)(timeout * 1000);
    self->baudrate = baochip_uart2_claim(baudrate, sigint_enabled);
    self->active = true;
}

bool common_hal_busio_uart_deinited(busio_uart_obj_t *self) {
    return !self->active;
}

void common_hal_busio_uart_deinit(busio_uart_obj_t *self) {
    if (common_hal_busio_uart_deinited(self)) {
        return;
    }
    self->active = false;
    baochip_uart2_release();
    common_hal_reset_pin(self->tx);
    common_hal_reset_pin(self->rx);
    self->tx = NULL;
    self->rx = NULL;
}

size_t common_hal_busio_uart_read(busio_uart_obj_t *self,
    uint8_t *data, size_t len, int *errcode) {
    if (self->rx == NULL) {
        mp_raise_ValueError_varg(MP_ERROR_TEXT("No %q pin"), MP_QSTR_rx);
    }
    if (len == 0) {
        return 0;
    }

    size_t total = 0;
    uint64_t start = supervisor_ticks_ms64();
    while (total < len) {
        int c = baochip_uart2_getc();
        if (c >= 0) {
            data[total++] = (uint8_t)c;
            start = supervisor_ticks_ms64();
            continue;
        }
        if (supervisor_ticks_ms64() - start >= self->timeout_ms) {
            break;
        }
        RUN_BACKGROUND_TASKS;
        if (mp_hal_is_interrupted()) {
            break;
        }
    }

    if (total == 0) {
        *errcode = MP_EAGAIN;
        return MP_STREAM_ERROR;
    }
    return total;
}

size_t common_hal_busio_uart_write(busio_uart_obj_t *self,
    const uint8_t *data, size_t len, int *errcode) {
    if (self->tx == NULL) {
        mp_raise_ValueError_varg(MP_ERROR_TEXT("No %q pin"), MP_QSTR_tx);
    }
    baochip_uart2_write(data, len);
    return len;
}

uint32_t common_hal_busio_uart_get_baudrate(busio_uart_obj_t *self) {
    return self->baudrate;
}

void common_hal_busio_uart_set_baudrate(busio_uart_obj_t *self, uint32_t baudrate) {
    self->baudrate = baochip_uart2_set_baudrate(baudrate);
}

mp_float_t common_hal_busio_uart_get_timeout(busio_uart_obj_t *self) {
    return (mp_float_t)(self->timeout_ms / 1000.0f);
}

void common_hal_busio_uart_set_timeout(busio_uart_obj_t *self, mp_float_t timeout) {
    self->timeout_ms = (uint32_t)(timeout * 1000);
}

uint32_t common_hal_busio_uart_rx_characters_available(busio_uart_obj_t *self) {
    return baochip_uart2_available();
}

void common_hal_busio_uart_clear_rx_buffer(busio_uart_obj_t *self) {
    baochip_uart2_clear();
}

bool common_hal_busio_uart_ready_to_tx(busio_uart_obj_t *self) {
    return self->tx != NULL;
}
