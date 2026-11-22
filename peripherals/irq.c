// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 MicroPython contributors
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

// Interrupt dispatch, used in place of the SDK's irq.c with the same API
// (hardware/irq.h). Adapted from baochip_irq.c in the MicroPython Baochip
// port by Andrew Leech. The handler runs before EV_PENDING is cleared,
// which the USB controller needs.

#include <stdint.h>
#include <stddef.h>

#include "hardware/irq.h"
#include "hardware/uart.h"
#include "hardware/regs/timer.h"
#include "boards/dabao.h"

static const uint32_t irq_array_base[20] = {
    0xE0004000, 0xE0005000, 0xE0010000, 0xE0011000, 0xE0012000,
    0xE0013000, 0xE0014000, 0xE0015000, 0xE0016000, 0xE0017000,
    0xE0006000, 0xE0007000, 0xE0008000, 0xE0009000, 0xE000A000,
    0xE000B000, 0xE000C000, 0xE000D000, 0xE000E000, 0xE000F000,
};

#define IRQ_EV_PENDING      0x10
#define IRQ_EV_ENABLE       0x14
#define IRQ_TABLE_SIZE      31

static irq_handler_t irq_handlers[IRQ_TABLE_SIZE];

extern uint32_t _trap_stack_top;

static inline uint32_t read_mim(void) {
    uint32_t val;
    __asm__ volatile ("csrr %0, 0xBC0" : "=r" (val));
    return val;
}

static inline void write_mim(uint32_t val) {
    __asm__ volatile ("csrw 0xBC0, %0" : : "r" (val));
}

static inline uint32_t read_mip(void) {
    uint32_t val;
    __asm__ volatile ("csrr %0, 0xFC0" : "=r" (val));
    return val;
}

void irq_init(void) {
    for (int i = 0; i < IRQ_TABLE_SIZE; i++) {
        irq_handlers[i] = NULL;
    }
    write_mim(0);
    __asm__ volatile ("csrs mie, %0" : : "r" (1 << 11));
    __asm__ volatile ("csrsi mstatus, 0x8");
}

void irq_set_handler(uint32_t irq_no, irq_handler_t handler) {
    if (irq_no < IRQ_TABLE_SIZE) {
        irq_handlers[irq_no] = handler;
    }
}

void irq_enable(uint32_t irq_no) {
    if (irq_no < 20) {
        *(volatile uint32_t *)(irq_array_base[irq_no] + IRQ_EV_ENABLE) = 0xFFFF;
    }
    write_mim(read_mim() | (1u << irq_no));
}

void irq_enable_events(uint32_t irq_no, uint32_t event_mask) {
    if (irq_no < 20) {
        *(volatile uint32_t *)(irq_array_base[irq_no] + IRQ_EV_ENABLE) |= event_mask;
    }
    write_mim(read_mim() | (1u << irq_no));
}

void irq_disable(uint32_t irq_no) {
    write_mim(read_mim() & ~(1u << irq_no));
}

static void fault_puts(const char *s) {
    uint32_t n = 0;
    while (s[n] != '\0') {
        n++;
    }
    uart_write(BAO_DEFAULT_UART, (const uint8_t *)s, n);
}

static void fault_put_hex(const char *label, uint32_t val) {
    static const char hexd[] = "0123456789abcdef";
    char buf[12];
    buf[0] = '0';
    buf[1] = 'x';
    for (int i = 0; i < 8; i++) {
        buf[2 + i] = hexd[(val >> ((7 - i) * 4)) & 0xF];
    }
    buf[10] = '\r';
    buf[11] = '\n';
    fault_puts(label);
    uart_write(BAO_DEFAULT_UART, (const uint8_t *)buf, sizeof(buf));
}

void trap_dispatch(void) {
    uint32_t mcause;
    __asm__ volatile ("csrr %0, mcause" : "=r" (mcause));

    if (mcause == 0x8000000B) {
        uint32_t pending = read_mip();

        if (pending & (1u << 30)) {
            TIMER0_EV_PENDING = 1;
            if (irq_handlers[30]) {
                irq_handlers[30](1);
            }
        }
        if (pending & (1u << 20)) {
            TICKTIMER_EV_PENDING = 1;
            if (irq_handlers[20]) {
                irq_handlers[20](1);
            }
        }
        for (int i = 0; i < 20; i++) {
            if (pending & (1u << i)) {
                volatile uint32_t *ev_pending =
                    (volatile uint32_t *)(irq_array_base[i] + IRQ_EV_PENDING);
                uint32_t events = *ev_pending;
                if (irq_handlers[i]) {
                    irq_handlers[i](events);
                }
                *ev_pending = events;
            }
        }
        __asm__ volatile ("csrs mie, %0" : : "r" (1 << 11));
        return;
    }

    uint32_t mepc, mtval;
    __asm__ volatile ("csrr %0, mepc" : "=r" (mepc));
    __asm__ volatile ("csrr %0, mtval" : "=r" (mtval));

    // ebreak is a failed TU_ASSERT. Step over it and carry on.
    if (mcause == 3) {
        uint32_t *frame = (uint32_t *)((uintptr_t)&_trap_stack_top - 36u * 4u);
        uint16_t insn = *(const uint16_t *)(uintptr_t)mepc;
        frame[31] = mepc + (((insn & 0x3u) == 0x3u) ? 4u : 2u);
        #if CIRCUITPY_PORT_SERIAL
        fault_put_hex("USB assert at ", mepc);
        #endif
        return;
    }

    // Anything else: report on UART2 and halt.
    uart_init(BAO_DEFAULT_UART, 115200);
    fault_puts("\r\n*** TRAP ***\r\n");
    fault_put_hex("  mcause=", mcause);
    fault_put_hex("  mepc  =", mepc);
    fault_put_hex("  mtval =", mtval);
    fault_puts("  halted\r\n");
    for (volatile int spin = 0; spin == 0; spin = 0) {
    }
}
