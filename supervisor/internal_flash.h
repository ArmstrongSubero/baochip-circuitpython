// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "py/mpconfig.h"

// CIRCUITPY lives in SRAM. RRAM is good for about 10,000 writes, so it is
// written only by baochip.save() and read back at boot.
#define INTERNAL_FLASH_FILESYSTEM_SIZE        (512 * 1024)
#define INTERNAL_FLASH_FILESYSTEM_NUM_BLOCKS  (INTERNAL_FLASH_FILESYSTEM_SIZE / FILESYSTEM_BLOCK_SIZE)

// Saved copy: one header page, then the disk image.
#define BAOCHIP_STORE_BASE      0x60160000u
#define BAOCHIP_STORE_PAGE      32u
#define BAOCHIP_STORE_DATA      (BAOCHIP_STORE_BASE + BAOCHIP_STORE_PAGE)
#define BAOCHIP_STORE_END       (BAOCHIP_STORE_DATA + INTERNAL_FLASH_FILESYSTEM_SIZE)

// Writes the pages that differ. Returns the count, or a negative value on
// failure. max_pages above zero stops early.
int32_t baochip_store_save(int32_t max_pages);

// Number of pages that differ between the disk and the saved copy.
int32_t baochip_store_pending(void);

// One soak round: write a pattern to every page and read it back.
int32_t baochip_store_soak_round(uint32_t round, uint32_t *write_errors, uint32_t *verify_errors);

// Checksum of the RRAM outside the store.
uint32_t baochip_store_guard_checksum(void);

