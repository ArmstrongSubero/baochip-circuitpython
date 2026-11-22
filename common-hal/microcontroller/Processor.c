// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include <math.h>
#include <string.h>

#include "common-hal/microcontroller/Processor.h"
#include "shared-bindings/microcontroller/Processor.h"
#include "shared-bindings/microcontroller/ResetReason.h"

#include "bao.h"

float common_hal_mcu_processor_get_temperature(void) {
    return NAN;
}

float common_hal_mcu_processor_get_voltage(void) {
    return NAN;
}

uint32_t common_hal_mcu_processor_get_frequency(void) {
    return cycles_per_us() * 1000000u;
}

// The uid is the public SERIAL_NUMBER data slot, or the UUID slot if that
// one is blank. Read only.
#define DATA_SLOT_BASE      0x603E0000u
#define DATA_SLOT_BYTES     32u
#define SLOT_SERIAL_NUMBER  0u
#define SLOT_UUID           1u

static bool read_slot(uint32_t slot, uint8_t out[]) {
    const volatile uint8_t *src =
        (const volatile uint8_t *)(DATA_SLOT_BASE + slot * DATA_SLOT_BYTES);
    bool all_zero = true;
    bool all_ones = true;
    for (uint32_t i = 0; i < COMMON_HAL_MCU_PROCESSOR_UID_LENGTH; i++) {
        out[i] = src[i];
        if (out[i] != 0x00) {
            all_zero = false;
        }
        if (out[i] != 0xFF) {
            all_ones = false;
        }
    }
    return !(all_zero || all_ones);
}

void common_hal_mcu_processor_get_uid(uint8_t raw_id[]) {
    if (read_slot(SLOT_SERIAL_NUMBER, raw_id)) {
        return;
    }
    if (read_slot(SLOT_UUID, raw_id)) {
        return;
    }
    memset(raw_id, 0, COMMON_HAL_MCU_PROCESSOR_UID_LENGTH);
}

mcu_reset_reason_t common_hal_mcu_processor_get_reset_reason(void) {
    return MCU_RESET_REASON_UNKNOWN;
}
