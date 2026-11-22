// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#pragma once

#include <stdint.h>

#define MICROPY_PY_SYS_PLATFORM             "Baochip-1x"
#define CIRCUITPY_DEFAULT_STACK_SIZE        (24 * 1024)
#define CIRCUITPY_PROCESSOR_COUNT           (1)
#define MICROPY_USE_INTERNAL_PRINTF         (1)

#define CIRCUITPY_USB_DEVICE_HIGH_SPEED     (1)

// PC13 is input only, and no pin can pull down.
#define CIRCUITPY_DIGITALIO_HAVE_INPUT_ONLY     (1)
#define CIRCUITPY_DIGITALIO_HAVE_INVALID_PULL   (1)

// The Corigine UDC driver is not in upstream TinyUSB. These come from its
// fork.
#define OPT_MCU_CORIGINE_BAO1X              9100
#define TUP_USBIP_CORIGINE_UDC
#define TUP_DCD_ENDPOINT_MAX                5
#define TUP_RHPORT_HIGHSPEED                1
#define TUP_DCD_EDPT_CLOSE_API

// PC13 shorts D+ and D- to ground on the Dabao. It is also the PROG pin.
#define TUD_CORIGINE_SE0_ASSERT() \
    do { gpio_set_dir(GPIO_PORT_C, 13, true); gpio_put(GPIO_PORT_C, 13, false); } while (0)
#define TUD_CORIGINE_SE0_DEASSERT() \
    do { gpio_put(GPIO_PORT_C, 13, true); gpio_set_dir(GPIO_PORT_C, 13, false); } while (0)

// The USB controller's DMA reaches IFRAM only.
#define TUD_CORIGINE_DMA_ATTR   __attribute__((section(".dma_buffers"), aligned(64)))

// Same endpoint numbers as the SDK's usb_cdc example.
#define USB_CDC_EP_NUM_NOTIFICATION         (1)
#define USB_CDC_EP_NUM_DATA_OUT             (2)
#define USB_CDC_EP_NUM_DATA_IN              (2)
#define USB_MSC_EP_NUM_OUT                  (3)
#define USB_MSC_EP_NUM_IN                   (3)

#include "py/circuitpy_mpconfig.h"
