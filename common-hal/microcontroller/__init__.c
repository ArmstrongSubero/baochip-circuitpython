// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/obj.h"
#include "py/mphal.h"
#include "common-hal/microcontroller/__init__.h"
#include "peripherals/pins.h"
#include "shared-bindings/microcontroller/__init__.h"
#include "shared-bindings/microcontroller/Pin.h"
#include "shared-bindings/microcontroller/Processor.h"
#include "supervisor/port.h"
#include "supervisor/shared/safe_mode.h"

#include "bao.h"
#include "bao_reset.h"

void common_hal_mcu_delay_us(uint32_t delay) {
    delay_us(delay);
}

static volatile uint32_t nesting_count = 0;
static uint32_t saved_mstatus = 0;

void common_hal_mcu_disable_interrupts(void) {
    uint32_t prev;
    __asm__ volatile ("csrrci %0, mstatus, 0x8" : "=r" (prev));
    if (nesting_count == 0) {
        saved_mstatus = prev;
    }
    nesting_count++;
}

void common_hal_mcu_enable_interrupts(void) {
    if (nesting_count == 0) {
        reset_into_safe_mode(SAFE_MODE_INTERRUPT_ERROR);
    }
    nesting_count--;
    if (nesting_count == 0 && (saved_mstatus & 0x8)) {
        __asm__ volatile ("csrsi mstatus, 0x8");
    }
}

static bool next_reset_to_bootloader = false;

void common_hal_mcu_on_next_reset(mcu_runmode_t runmode) {
    if (runmode == RUNMODE_SAFE_MODE) {
        safe_mode_on_next_reset(SAFE_MODE_PROGRAMMATIC);
    }
    next_reset_to_bootloader = (runmode == RUNMODE_BOOTLOADER);
}

void common_hal_mcu_reset(void) {
    if (next_reset_to_bootloader) {
        reset_to_bootloader();
    }
    reset_cpu();
}

const mcu_processor_obj_t common_hal_mcu_processor_obj = {
    .base = {
        .type = &mcu_processor_type,
    },
};

static const mp_rom_map_elem_t mcu_pin_global_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_PB0), MP_ROM_PTR(&pin_PB0) },
    { MP_ROM_QSTR(MP_QSTR_PB1), MP_ROM_PTR(&pin_PB1) },
    { MP_ROM_QSTR(MP_QSTR_PB2), MP_ROM_PTR(&pin_PB2) },
    { MP_ROM_QSTR(MP_QSTR_PB3), MP_ROM_PTR(&pin_PB3) },
    { MP_ROM_QSTR(MP_QSTR_PB4), MP_ROM_PTR(&pin_PB4) },
    { MP_ROM_QSTR(MP_QSTR_PB5), MP_ROM_PTR(&pin_PB5) },
    { MP_ROM_QSTR(MP_QSTR_PB6), MP_ROM_PTR(&pin_PB6) },
    { MP_ROM_QSTR(MP_QSTR_PB7), MP_ROM_PTR(&pin_PB7) },
    { MP_ROM_QSTR(MP_QSTR_PB8), MP_ROM_PTR(&pin_PB8) },
    { MP_ROM_QSTR(MP_QSTR_PB9), MP_ROM_PTR(&pin_PB9) },
    { MP_ROM_QSTR(MP_QSTR_PB10), MP_ROM_PTR(&pin_PB10) },
    { MP_ROM_QSTR(MP_QSTR_PB11), MP_ROM_PTR(&pin_PB11) },
    { MP_ROM_QSTR(MP_QSTR_PB12), MP_ROM_PTR(&pin_PB12) },
    { MP_ROM_QSTR(MP_QSTR_PB13), MP_ROM_PTR(&pin_PB13) },
    { MP_ROM_QSTR(MP_QSTR_PB14), MP_ROM_PTR(&pin_PB14) },
    { MP_ROM_QSTR(MP_QSTR_PB15), MP_ROM_PTR(&pin_PB15) },
    { MP_ROM_QSTR(MP_QSTR_PC0), MP_ROM_PTR(&pin_PC0) },
    { MP_ROM_QSTR(MP_QSTR_PC1), MP_ROM_PTR(&pin_PC1) },
    { MP_ROM_QSTR(MP_QSTR_PC2), MP_ROM_PTR(&pin_PC2) },
    { MP_ROM_QSTR(MP_QSTR_PC3), MP_ROM_PTR(&pin_PC3) },
    { MP_ROM_QSTR(MP_QSTR_PC4), MP_ROM_PTR(&pin_PC4) },
    { MP_ROM_QSTR(MP_QSTR_PC5), MP_ROM_PTR(&pin_PC5) },
    { MP_ROM_QSTR(MP_QSTR_PC6), MP_ROM_PTR(&pin_PC6) },
    { MP_ROM_QSTR(MP_QSTR_PC7), MP_ROM_PTR(&pin_PC7) },
    { MP_ROM_QSTR(MP_QSTR_PC8), MP_ROM_PTR(&pin_PC8) },
    { MP_ROM_QSTR(MP_QSTR_PC9), MP_ROM_PTR(&pin_PC9) },
    { MP_ROM_QSTR(MP_QSTR_PC10), MP_ROM_PTR(&pin_PC10) },
    { MP_ROM_QSTR(MP_QSTR_PC11), MP_ROM_PTR(&pin_PC11) },
    { MP_ROM_QSTR(MP_QSTR_PC12), MP_ROM_PTR(&pin_PC12) },
    { MP_ROM_QSTR(MP_QSTR_PC14), MP_ROM_PTR(&pin_PC14) },
    { MP_ROM_QSTR(MP_QSTR_PC15), MP_ROM_PTR(&pin_PC15) },
};
MP_DEFINE_CONST_DICT(mcu_pin_globals, mcu_pin_global_dict_table);
