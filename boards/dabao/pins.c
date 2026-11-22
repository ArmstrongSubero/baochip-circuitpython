// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

// Header pins as labelled on the Dabao, plus the usual bus aliases.

#include "shared-bindings/board/__init__.h"

static const mp_rom_map_elem_t board_module_globals_table[] = {
    CIRCUITPYTHON_BOARD_DICT_STANDARD_ITEMS

    { MP_ROM_QSTR(MP_QSTR_PB1), MP_ROM_PTR(&pin_PB1) },
    { MP_ROM_QSTR(MP_QSTR_PB2), MP_ROM_PTR(&pin_PB2) },
    { MP_ROM_QSTR(MP_QSTR_PB3), MP_ROM_PTR(&pin_PB3) },
    { MP_ROM_QSTR(MP_QSTR_PB4), MP_ROM_PTR(&pin_PB4) },
    { MP_ROM_QSTR(MP_QSTR_PB5), MP_ROM_PTR(&pin_PB5) },
    { MP_ROM_QSTR(MP_QSTR_PB11), MP_ROM_PTR(&pin_PB11) },
    { MP_ROM_QSTR(MP_QSTR_PB12), MP_ROM_PTR(&pin_PB12) },
    { MP_ROM_QSTR(MP_QSTR_PB13), MP_ROM_PTR(&pin_PB13) },
    { MP_ROM_QSTR(MP_QSTR_PB14), MP_ROM_PTR(&pin_PB14) },
    { MP_ROM_QSTR(MP_QSTR_PC0), MP_ROM_PTR(&pin_PC0) },
    { MP_ROM_QSTR(MP_QSTR_PC1), MP_ROM_PTR(&pin_PC1) },
    { MP_ROM_QSTR(MP_QSTR_PC2), MP_ROM_PTR(&pin_PC2) },
    { MP_ROM_QSTR(MP_QSTR_PC3), MP_ROM_PTR(&pin_PC3) },
    { MP_ROM_QSTR(MP_QSTR_PC7), MP_ROM_PTR(&pin_PC7) },
    { MP_ROM_QSTR(MP_QSTR_PC8), MP_ROM_PTR(&pin_PC8) },
    { MP_ROM_QSTR(MP_QSTR_PC9), MP_ROM_PTR(&pin_PC9) },
    { MP_ROM_QSTR(MP_QSTR_PC10), MP_ROM_PTR(&pin_PC10) },
    { MP_ROM_QSTR(MP_QSTR_PC11), MP_ROM_PTR(&pin_PC11) },
    { MP_ROM_QSTR(MP_QSTR_PC12), MP_ROM_PTR(&pin_PC12) },

    { MP_ROM_QSTR(MP_QSTR_TX), MP_ROM_PTR(&pin_PB14) },
    { MP_ROM_QSTR(MP_QSTR_RX), MP_ROM_PTR(&pin_PB13) },
    { MP_ROM_QSTR(MP_QSTR_SCL), MP_ROM_PTR(&pin_PB11) },
    { MP_ROM_QSTR(MP_QSTR_SDA), MP_ROM_PTR(&pin_PB12) },
    { MP_ROM_QSTR(MP_QSTR_SCK), MP_ROM_PTR(&pin_PC0) },
    { MP_ROM_QSTR(MP_QSTR_MOSI), MP_ROM_PTR(&pin_PC1) },
    { MP_ROM_QSTR(MP_QSTR_MISO), MP_ROM_PTR(&pin_PC2) },
    { MP_ROM_QSTR(MP_QSTR_CS), MP_ROM_PTR(&pin_PC3) },
    { MP_ROM_QSTR(MP_QSTR_A0), MP_ROM_PTR(&pin_PC9) },
};

MP_DEFINE_CONST_DICT(board_module_globals, board_module_globals_table);
