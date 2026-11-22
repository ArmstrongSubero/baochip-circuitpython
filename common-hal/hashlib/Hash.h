// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#pragma once

#include "py/obj.h"

#include "hardware/sha.h"

typedef struct {
    mp_obj_base_t base;
    sha2_stream_t stream;
    uint8_t digest_size;
} hashlib_hash_obj_t;
