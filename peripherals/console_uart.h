// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
//
// SPDX-License-Identifier: MIT

#pragma once

#include <stdbool.h>
#include <stdint.h>

// UART2 belongs to busio.UART. In a build with the REPL on UART2,
// busio.UART borrows it.
#define BAOCHIP_CONSOLE_BAUDRATE    115200

void baochip_uart2_idle_pins(void);

bool baochip_uart2_claimed(void);
uint32_t baochip_uart2_claim(uint32_t baudrate, bool sigint_enabled);
void baochip_uart2_release(void);
uint32_t baochip_uart2_set_baudrate(uint32_t baudrate);
uint32_t baochip_uart2_available(void);
int baochip_uart2_getc(void);
void baochip_uart2_clear(void);
void baochip_uart2_write(const uint8_t *data, uint32_t len);
