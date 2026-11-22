# This file is part of the CircuitPython project: https://circuitpython.org
#
# SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
#
# SPDX-License-Identifier: MIT

USB_VID = 0x1209
USB_PID = 0x0001
USB_PRODUCT = "Dabao"
USB_MANUFACTURER = "Rovari"

# Frozen libraries. asyncio needs adafruit_ticks.
FROZEN_MPY_DIRS += $(TOP)/frozen/Adafruit_CircuitPython_asyncio
FROZEN_MPY_DIRS += $(TOP)/frozen/Adafruit_CircuitPython_Ticks
FROZEN_MPY_DIRS += $(TOP)/frozen/Adafruit_CircuitPython_Register
FROZEN_MPY_DIRS += $(TOP)/frozen/Adafruit_CircuitPython_SimpleIO
FROZEN_MPY_DIRS += $(TOP)/frozen/Adafruit_CircuitPython_Motor
