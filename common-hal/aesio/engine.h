// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

// The SDK's aes.h and aesio both define AES_MODE_*, with different values.
// SDK calls stay behind these.

#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

int baochip_aes_load(const uint8_t *key, uint32_t key_length, const uint8_t *iv);
int baochip_aes_ecb(bool encrypt, uint8_t *buffer, size_t length);
int baochip_aes_cbc(bool encrypt, uint8_t *buffer, size_t length);
