// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "supervisor/usb.h"
#include "supervisor/port.h"
#include "shared-bindings/microcontroller/__init__.h"

#include "bao.h"
#include "hardware/irq.h"
#include "dcd_corigine_udc.h"
#include "udc_regs.h"

// The USB interrupt is IRQ array 1.
static void usb_array_handler(uint32_t pending) {
    (void)pending;
    usb_irq_handler(0);
}

void init_usb_hardware(void) {
    irq_set_handler(UDC_IRQARRAY, usb_array_handler);
}

// The controller can stop interrupting while events queue up, so it is
// also polled from the background task.
void baochip_usb_poll(void) {
    common_hal_mcu_disable_interrupts();
    dcd_corigine_poll_pending_events(0);
    common_hal_mcu_enable_interrupts();
    usb_background_schedule();
}

uint32_t tusb_time_millis_api(void) {
    return (uint32_t)millis();
}
