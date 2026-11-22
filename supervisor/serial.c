// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/mphal.h"
#include "py/runtime.h"
#include "shared/runtime/interrupt_char.h"
#include "shared-bindings/microcontroller/__init__.h"
#include "supervisor/shared/serial.h"

#include "bao.h"
#include "hardware/gpio.h"
#include "hardware/irq.h"
#include "hardware/regs/addressmap.h"
#include "hardware/regs/udma.h"

#include "peripherals/console_uart.h"

// UART2 on PB14 (TX) and PB13 (RX), interrupt driven into a ring buffer.
// The receive setup follows the MicroPython Baochip port by Andrew Leech.

#define RX_BUF_SIZE     1024
#define UART_REG(off)   (*(volatile uint32_t *)(UDMA_UART2_BASE + (off)))

static volatile uint8_t rx_buf[RX_BUF_SIZE];
static volatile uint32_t rx_head;
static volatile uint32_t rx_tail;
static volatile uint32_t rx_dropped;

// Set while busio.UART owns the port.
static bool busio_owns;
static bool busio_sigint;

static void uart_rx_drain(void) {
    while (UART_REG(UDMA_UART_VALID_OFFSET) & 1u) {
        uint8_t ch = (uint8_t)(UART_REG(UDMA_UART_DATA_OFFSET) & 0xFFu);
        if ((!busio_owns || busio_sigint) && (int)ch == mp_interrupt_char) {
            mp_sched_keyboard_interrupt();
            continue;
        }
        uint32_t next = (rx_head + 1) % RX_BUF_SIZE;
        if (next == rx_tail) {
            rx_dropped++;
            continue;
        }
        rx_buf[rx_head] = ch;
        rx_head = next;
    }
}

static void uart_rx_handler(uint32_t pending) {
    if (pending & UART2_EVT_RX_CHAR) {
        uart_rx_drain();
    }
    if (pending & UART2_EVT_ERR) {
        (void)UART_REG(UDMA_UART_ERROR_OFFSET);
        rx_dropped++;
    }
}

// A byte already waiting when the interrupt is armed raises no event.
static void uart_rx_poll(void) {
    common_hal_mcu_disable_interrupts();
    uart_rx_drain();
    common_hal_mcu_enable_interrupts();
}

// SETUP bit 4 is polling mode. Clear it to get rx_char events.
static void uart_rx_arm(void) {
    UART_REG(UDMA_UART_SETUP_OFFSET) &= ~(1u << 4);
    UART_REG(UDMA_UART_IRQ_EN_OFFSET) = (1u << 0) | (1u << 1);
}

static uint32_t rx_count(void) {
    uart_rx_poll();
    return (rx_head + RX_BUF_SIZE - rx_tail) % RX_BUF_SIZE;
}

static int rx_pop(void) {
    uart_rx_poll();
    if (rx_head == rx_tail) {
        return -1;
    }
    int c = rx_buf[rx_tail];
    rx_tail = (rx_tail + 1) % RX_BUF_SIZE;
    return c;
}

// Send in short chunks.
#define TX_CHUNK    64

static void tx_write(const uint8_t *data, uint32_t len) {
    while (len > 0) {
        uint32_t n = len > TX_CHUNK ? TX_CHUNK : len;
        uart_write(BAO_DEFAULT_UART, data, n);
        data += n;
        len -= n;
    }
}

static void uart_rx_start(void) {
    rx_head = 0;
    rx_tail = 0;
    uart_rx_arm();
    irq_set_handler(IRQ_UART, uart_rx_handler);
    irq_enable_events(IRQ_UART, UART2_EVT_RX_CHAR | UART2_EVT_ERR);
}

// Unclaimed pins must not drive.
void baochip_uart2_idle_pins(void) {
    #if !CIRCUITPY_PORT_SERIAL
    UART_REG(UDMA_UART_IRQ_EN_OFFSET) = 0;
    gpio_init(GPIO_PORT_B, 13);
    gpio_init(GPIO_PORT_B, 14);
    #endif
}

void port_serial_early_init(void) {
}

void port_serial_init(void) {
    busio_owns = false;
    uart_rx_start();
}

bool port_serial_connected(void) {
    return !busio_owns;
}

char port_serial_read(void) {
    if (busio_owns) {
        return -1;
    }
    return (char)rx_pop();
}

uint32_t port_serial_bytes_available(void) {
    if (busio_owns) {
        return 0;
    }
    return rx_count();
}

void port_serial_write_substring(const char *text, uint32_t len) {
    if (busio_owns) {
        return;
    }
    tx_write((const uint8_t *)text, len);
}

bool baochip_uart2_claimed(void) {
    return busio_owns;
}

uint32_t baochip_uart2_set_baudrate(uint32_t baudrate) {
    common_hal_mcu_disable_interrupts();
    uint32_t actual = uart_init(BAO_DEFAULT_UART, baudrate);
    uart_rx_arm();
    common_hal_mcu_enable_interrupts();
    return actual;
}

uint32_t baochip_uart2_claim(uint32_t baudrate, bool sigint_enabled) {
    busio_owns = true;
    busio_sigint = sigint_enabled;
    #if !CIRCUITPY_PORT_SERIAL
    uart_rx_start();
    #endif
    uint32_t actual = baochip_uart2_set_baudrate(baudrate);
    baochip_uart2_clear();
    return actual;
}

void baochip_uart2_release(void) {
    if (!busio_owns) {
        return;
    }
    #if CIRCUITPY_PORT_SERIAL
    baochip_uart2_set_baudrate(BAOCHIP_CONSOLE_BAUDRATE);
    #else
    irq_disable(IRQ_UART);
    UART_REG(UDMA_UART_IRQ_EN_OFFSET) = 0;
    #endif
    baochip_uart2_clear();
    busio_owns = false;
}

uint32_t baochip_uart2_available(void) {
    return rx_count();
}

int baochip_uart2_getc(void) {
    return rx_pop();
}

void baochip_uart2_clear(void) {
    common_hal_mcu_disable_interrupts();
    while (UART_REG(UDMA_UART_VALID_OFFSET) & 1u) {
        (void)UART_REG(UDMA_UART_DATA_OFFSET);
    }
    rx_head = 0;
    rx_tail = 0;
    common_hal_mcu_enable_interrupts();
}

void baochip_uart2_write(const uint8_t *data, uint32_t len) {
    tx_write(data, len);
}
