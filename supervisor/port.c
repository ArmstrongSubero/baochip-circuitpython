// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include <stdint.h>

#include "supervisor/background_callback.h"
#include "supervisor/board.h"
#include "supervisor/port.h"
#include "supervisor/shared/tick.h"
#include "common-hal/microcontroller/Pin.h"
#include "peripherals/console_uart.h"

#if CIRCUITPY_PWMIO
#include "common-hal/pwmio/PWMOut.h"
#endif

void baochip_i2c_reset(void);
void baochip_spi_reset(void);

#include "bao.h"
#include "bao_reset.h"
#include "hardware/irq.h"

#if CIRCUITPY_USB_DEVICE
#include "dcd_corigine_udc.h"
#endif

extern uint32_t _heap_start, _heap_end;
extern uint32_t _main_stack_top, _stack_limit;
extern uint32_t _saved_word;

// The SDK tick is 1 ms. CircuitPython counts in 1/1024 s.
static uint64_t ms_to_ticks(uint64_t ms, uint8_t *subticks) {
    uint64_t sub = (ms * 32768u) / 1000u;
    if (subticks != NULL) {
        *subticks = (uint8_t)(sub & 0x1F);
    }
    return sub >> 5;
}

safe_mode_t port_init(void) {
    bao_init();
    irq_init();
    baochip_uart2_idle_pins();
    return SAFE_MODE_NONE;
}

void reset_port(void) {
    #if CIRCUITPY_BUSIO
    baochip_uart2_release();
    baochip_i2c_reset();
    baochip_spi_reset();
    #endif
    #if CIRCUITPY_PWMIO
    baochip_pwmout_reset();
    #endif
    reset_all_pins();
}

void reset_cpu(void) {
    #if CIRCUITPY_USB_DEVICE
    // Disconnect cleanly and release PC13 before the reset.
    dcd_corigine_teardown(0);
    gpio_put(GPIO_PORT_C, 13, true);
    gpio_set_dir(GPIO_PORT_C, 13, false);
    #endif
    bao_software_reset();
    while (true) {
    }
}

void reset_to_bootloader(void) {
    // PC13 held low across the reset keeps boot1 in flashing mode.
    #if CIRCUITPY_USB_DEVICE
    dcd_corigine_teardown(0);
    #endif
    gpio_init(GPIO_PORT_C, 13);
    gpio_put(GPIO_PORT_C, 13, false);
    gpio_set_dir(GPIO_PORT_C, 13, true);
    delay_us(1000);
    bao_software_reset();
    while (true) {
    }
}

uint32_t *port_heap_get_bottom(void) {
    return &_heap_start;
}

uint32_t *port_heap_get_top(void) {
    return &_heap_end;
}

uint32_t *port_stack_get_limit(void) {
    return &_stack_limit;
}

uint32_t *port_stack_get_top(void) {
    return &_main_stack_top;
}

void port_set_saved_word(uint32_t value) {
    _saved_word = value;
}

uint32_t port_get_saved_word(void) {
    return _saved_word;
}

uint64_t port_get_raw_ticks(uint8_t *subticks) {
    return ms_to_ticks(millis(), subticks);
}

void port_enable_tick(void) {
}

void port_disable_tick(void) {
}

// No timer interrupt, so sleeping is a busy wait.
void port_interrupt_after_ticks(uint32_t ticks) {
    (void)ticks;
}

void port_idle_until_interrupt(void) {
}

void port_boot_info(void) {
}
