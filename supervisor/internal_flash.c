// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#include "supervisor/internal_flash.h"

#include <stdint.h>
#include <string.h>

#include "extmod/vfs.h"
#include "extmod/vfs_fat.h"
#include "py/mphal.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "lib/oofatfs/ff.h"
#include "supervisor/flash.h"
#include "supervisor/shared/internal_flash.h"

#include "hardware/rram.h"

#define STORE_MAGIC     0x59504342u
#define STORE_VERSION   1u

typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t size;
    uint32_t reserved[5];
} store_header_t;

_Static_assert(sizeof(store_header_t) == BAOCHIP_STORE_PAGE, "header is one page");
_Static_assert((BAOCHIP_STORE_BASE % BAOCHIP_STORE_PAGE) == 0, "store is page aligned");
_Static_assert(BAOCHIP_STORE_BASE >= RRAM_USER_BASE, "store starts in runtime storage");
_Static_assert(BAOCHIP_STORE_END <= RRAM_USER_TOP, "store ends below the security region");
_Static_assert((INTERNAL_FLASH_FILESYSTEM_SIZE % BAOCHIP_STORE_PAGE) == 0, "disk is whole pages");

static uint8_t ram_disk[INTERNAL_FLASH_FILESYSTEM_SIZE];
static bool loaded;

static const store_header_t wanted_header = {
    .magic = STORE_MAGIC,
    .version = STORE_VERSION,
    .size = INTERNAL_FLASH_FILESYSTEM_SIZE,
};

static bool page_differs(uint32_t addr, const uint8_t *data) {
    return memcmp((const void *)(uintptr_t)addr, data, BAOCHIP_STORE_PAGE) != 0;
}

// Never write outside the store.
static int write_page(uint32_t addr, const uint8_t *data) {
    if (addr < BAOCHIP_STORE_BASE || addr > BAOCHIP_STORE_END - BAOCHIP_STORE_PAGE) {
        return -1;
    }
    if ((addr % BAOCHIP_STORE_PAGE) != 0) {
        return -1;
    }
    uint8_t page[BAOCHIP_STORE_PAGE];
    memcpy(page, data, BAOCHIP_STORE_PAGE);
    return rram_write_page(addr, page);
}

void supervisor_flash_init(void) {
    if (loaded) {
        return;
    }
    loaded = true;
    store_header_t header;
    memcpy(&header, (const void *)(uintptr_t)BAOCHIP_STORE_BASE, sizeof(header));
    if (header.magic == STORE_MAGIC && header.version == STORE_VERSION &&
        header.size == INTERNAL_FLASH_FILESYSTEM_SIZE) {
        memcpy(ram_disk, (const void *)(uintptr_t)BAOCHIP_STORE_DATA, INTERNAL_FLASH_FILESYSTEM_SIZE);
    }
}

int32_t baochip_store_pending(void) {
    int32_t count = 0;
    if (page_differs(BAOCHIP_STORE_BASE, (const uint8_t *)&wanted_header)) {
        count++;
    }
    for (uint32_t off = 0; off < INTERNAL_FLASH_FILESYSTEM_SIZE; off += BAOCHIP_STORE_PAGE) {
        if (page_differs(BAOCHIP_STORE_DATA + off, &ram_disk[off])) {
            count++;
        }
    }
    return count;
}

int32_t baochip_store_save(int32_t max_pages) {
    int32_t written = 0;
    for (uint32_t off = 0; off < INTERNAL_FLASH_FILESYSTEM_SIZE; off += BAOCHIP_STORE_PAGE) {
        uint32_t addr = BAOCHIP_STORE_DATA + off;
        if (!page_differs(addr, &ram_disk[off])) {
            continue;
        }
        if (max_pages > 0 && written >= max_pages) {
            return written;
        }
        if (write_page(addr, &ram_disk[off]) != 0) {
            return -1;
        }
        written++;
        // Keep USB alive during a long save.
        if ((written % 256) == 0) {
            RUN_BACKGROUND_TASKS;
        }
    }
    // Header last, so a first save that is cut short leaves no valid copy.
    if (page_differs(BAOCHIP_STORE_BASE, (const uint8_t *)&wanted_header)) {
        if (max_pages > 0 && written >= max_pages) {
            return written;
        }
        if (write_page(BAOCHIP_STORE_BASE, (const uint8_t *)&wanted_header) != 0) {
            return -1;
        }
        written++;
    }
    return written;
}

static void soak_pattern(uint32_t round, uint32_t page, uint8_t *out) {
    uint32_t x = (round + 1u) * 0x9E3779B1u ^ (page + 1u) * 0x85EBCA6Bu;
    for (uint32_t i = 0; i < BAOCHIP_STORE_PAGE; i++) {
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        out[i] = (uint8_t)(x >> 24);
    }
}

int32_t baochip_store_soak_round(uint32_t round, uint32_t *write_errors, uint32_t *verify_errors) {
    const uint32_t pages = (BAOCHIP_STORE_END - BAOCHIP_STORE_BASE) / BAOCHIP_STORE_PAGE;
    uint8_t pattern[BAOCHIP_STORE_PAGE];
    int32_t written = 0;

    for (uint32_t page = 0; page < pages; page++) {
        soak_pattern(round, page, pattern);
        if (write_page(BAOCHIP_STORE_BASE + page * BAOCHIP_STORE_PAGE, pattern) != 0) {
            (*write_errors)++;
        }
        written++;
        if ((page % 256u) == 255u) {
            RUN_BACKGROUND_TASKS;
        }
    }
    // Verify after all writes, to catch a page disturbed by a later one.
    for (uint32_t page = 0; page < pages; page++) {
        soak_pattern(round, page, pattern);
        if (page_differs(BAOCHIP_STORE_BASE + page * BAOCHIP_STORE_PAGE, pattern)) {
            (*verify_errors)++;
        }
    }
    RUN_BACKGROUND_TASKS;
    return written;
}

extern const uint8_t _program_start[];
extern const uint8_t _image_end[];

static uint32_t fnv1a(uint32_t hash, const uint8_t *start, const uint8_t *end) {
    for (const uint8_t *p = start; p < end; p++) {
        hash = (hash ^ *p) * 16777619u;
    }
    return hash;
}

uint32_t baochip_store_guard_checksum(void) {
    uint32_t hash = 2166136261u;
    hash = fnv1a(hash, _program_start, _image_end);
    hash = fnv1a(hash, (const uint8_t *)(uintptr_t)BAOCHIP_STORE_END,
        (const uint8_t *)(uintptr_t)RRAM_USER_TOP);
    return hash;
}

uint32_t supervisor_flash_get_block_size(void) {
    return FILESYSTEM_BLOCK_SIZE;
}

uint32_t supervisor_flash_get_block_count(void) {
    return INTERNAL_FLASH_FILESYSTEM_NUM_BLOCKS;
}

void port_internal_flash_flush(void) {
}

mp_uint_t supervisor_flash_read_blocks(uint8_t *dest, uint32_t block, uint32_t num_blocks) {
    if (block + num_blocks > INTERNAL_FLASH_FILESYSTEM_NUM_BLOCKS) {
        return 1;
    }
    memcpy(dest, &ram_disk[block * FILESYSTEM_BLOCK_SIZE], num_blocks * FILESYSTEM_BLOCK_SIZE);
    return 0;
}

mp_uint_t supervisor_flash_write_blocks(const uint8_t *src, uint32_t block, uint32_t num_blocks) {
    if (block + num_blocks > INTERNAL_FLASH_FILESYSTEM_NUM_BLOCKS) {
        return 1;
    }
    memcpy(&ram_disk[block * FILESYSTEM_BLOCK_SIZE], src, num_blocks * FILESYSTEM_BLOCK_SIZE);
    return 0;
}

void supervisor_flash_release_cache(void) {
}
