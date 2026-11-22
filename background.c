// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/runtime.h"
#include "supervisor/port.h"

#if CIRCUITPY_USB_DEVICE
void baochip_usb_poll(void);
#endif

void port_background_tick(void) {
}

void port_background_task(void) {
    #if CIRCUITPY_USB_DEVICE
    baochip_usb_poll();
    #endif
}

void port_start_background_tick(void) {
}

void port_finish_background_tick(void) {
}
