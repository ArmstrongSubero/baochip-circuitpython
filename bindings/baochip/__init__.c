// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "py/obj.h"
#include "py/runtime.h"
#include "py/mperrno.h"
#include "py/mphal.h"
#include "shared/runtime/interrupt_char.h"
#include "supervisor/shared/tick.h"

#include "supervisor/filesystem.h"
#include "supervisor/internal_flash.h"

//| """Baochip-1x specific functions
//|
//| CIRCUITPY lives in RAM on this chip, because its RRAM is rated for about
//| 10,000 write cycles. Files are lost at reset unless they are saved."""
//|
//| def save(max_pages: int = 0) -> int:
//|     """Copy CIRCUITPY to RRAM so it is there after a reset. Only the
//|     pages that changed are written. Returns the number of 32 byte pages
//|     written.
//|
//|     ``max_pages`` stops after that many pages. The copy is complete only
//|     once `pending` is zero."""
//|     ...
//|
static mp_obj_t baochip_save(size_t n_args, const mp_obj_t *args) {
    mp_int_t max_pages = 0;
    if (n_args > 0) {
        max_pages = mp_obj_get_int(args[0]);
        if (max_pages < 0) {
            mp_raise_ValueError(NULL);
        }
    }
    filesystem_flush();
    int32_t written = baochip_store_save((int32_t)max_pages);
    if (written < 0) {
        mp_raise_OSError(MP_EIO);
    }
    return MP_OBJ_NEW_SMALL_INT(written);
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(baochip_save_obj, 0, 1, baochip_save);

//| def pending() -> int:
//|     """Number of 32 byte pages that differ from the saved copy. Zero
//|     means everything on CIRCUITPY is already saved. Writes nothing."""
//|     ...
//|
static mp_obj_t baochip_pending(void) {
    filesystem_flush();
    return MP_OBJ_NEW_SMALL_INT(baochip_store_pending());
}
static MP_DEFINE_CONST_FUN_OBJ_0(baochip_pending_obj, baochip_pending);

//| def soak(rounds: int) -> tuple:
//|     """Endurance test of the RRAM store, for a board set aside for testing.
//|
//|     Each round writes a fresh pattern to every page of the store and reads
//|     it all back, then the firmware image and the rest of runtime storage
//|     are checked for changes. The saved copy of CIRCUITPY is put back at
//|     the end. Costs ``rounds + 1`` write cycles on every page of the store.
//|     Ctrl C stops it after the current round.
//|
//|     Returns ``(rounds done, pages written, write errors, verify errors,
//|     guard intact)``."""
//|     ...
//|
#define BAOCHIP_SOAK_MAX_ROUNDS 200

static mp_obj_t baochip_soak(mp_obj_t rounds_in) {
    mp_int_t rounds = mp_obj_get_int(rounds_in);
    if (rounds < 1 || rounds > BAOCHIP_SOAK_MAX_ROUNDS) {
        mp_raise_ValueError(NULL);
    }
    filesystem_flush();

    const uint32_t guard_before = baochip_store_guard_checksum();
    uint32_t write_errors = 0;
    uint32_t verify_errors = 0;
    uint32_t pages = 0;
    bool guard_ok = true;
    mp_int_t done = 0;

    for (mp_int_t r = 0; r < rounds; r++) {
        uint64_t t0 = supervisor_ticks_ms64();
        pages += (uint32_t)baochip_store_soak_round((uint32_t)r, &write_errors, &verify_errors);
        guard_ok = guard_ok && (baochip_store_guard_checksum() == guard_before);
        done++;
        mp_printf(&mp_plat_print, "round %d of %d: %d ms, write errors %d, verify errors %d, guard %s\n",
            (int)done, (int)rounds, (int)(supervisor_ticks_ms64() - t0),
            (int)write_errors, (int)verify_errors, guard_ok ? "ok" : "CHANGED");
        if (!guard_ok || mp_hal_is_interrupted()) {
            break;
        }
    }

    // Put the real copy of the drive back.
    int32_t restored = baochip_store_save(0);
    guard_ok = guard_ok && (baochip_store_guard_checksum() == guard_before);
    mp_printf(&mp_plat_print, "restored the saved drive: %d pages, pending %d, guard %s\n",
        (int)restored, (int)baochip_store_pending(), guard_ok ? "ok" : "CHANGED");

    mp_obj_t items[5] = {
        MP_OBJ_NEW_SMALL_INT(done),
        mp_obj_new_int_from_uint(pages),
        mp_obj_new_int_from_uint(write_errors),
        mp_obj_new_int_from_uint(verify_errors),
        mp_obj_new_bool(guard_ok),
    };
    return mp_obj_new_tuple(5, items);
}
static MP_DEFINE_CONST_FUN_OBJ_1(baochip_soak_obj, baochip_soak);

static const mp_rom_map_elem_t baochip_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_baochip) },
    { MP_ROM_QSTR(MP_QSTR_save), MP_ROM_PTR(&baochip_save_obj) },
    { MP_ROM_QSTR(MP_QSTR_pending), MP_ROM_PTR(&baochip_pending_obj) },
    { MP_ROM_QSTR(MP_QSTR_soak), MP_ROM_PTR(&baochip_soak_obj) },
};
static MP_DEFINE_CONST_DICT(baochip_module_globals, baochip_module_globals_table);

const mp_obj_module_t baochip_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&baochip_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_baochip, baochip_module);
