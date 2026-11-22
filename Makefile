# This file is part of the CircuitPython project: https://circuitpython.org
#
# SPDX-FileCopyrightText: Copyright (c) 2026 Armstrong Subero
#
# SPDX-License-Identifier: MIT

# Set DABAO_SDK to the Dabao SDK folder, or keep the SDK beside this repo.

BOARD ?= dabao
CROSS_COMPILE ?= riscv-none-elf-

include ../../py/circuitpy_mkenv.mk

DABAO_SDK ?= $(TOP)/../dabao-sdk-main
SDK := $(abspath $(DABAO_SDK))

ifeq ($(wildcard $(SDK)/src/common/bao_base/include/bao.h),)
$(error Dabao SDK not found at $(SDK). Set DABAO_SDK)
endif

INC += \
	-I. \
	-I../.. \
	-I../../lib/mp-readline \
	-I../../lib/tinyusb/src \
	-I../../supervisor/shared/usb \
	-Iboards/$(BOARD) \
	-Iusb/corigine \
	-Iboards \
	-I$(BUILD) \
	-I$(SDK)/src/common/bao_base/include \
	-I$(SDK)/src/common/bao_stdlib/include \
	-I$(SDK)/src/bao1x/hardware_regs/include \
	-I$(SDK)/src/bao1x/hardware_gpio/include \
	-I$(SDK)/src/bao1x/hardware_uart/include \
	-I$(SDK)/src/bao1x/hardware_i2c/include \
	-I$(SDK)/src/bao1x/hardware_spi/include \
	-I$(SDK)/src/bao1x/hardware_pwm/include \
	-I$(SDK)/src/bao1x/hardware_adc/include \
	-I$(SDK)/src/bao1x/hardware_trng/include \
	-I$(SDK)/src/bao1x/hardware_sha/include \
	-I$(SDK)/src/bao1x/hardware_aes/include \
	-I$(SDK)/src/bao1x/hardware_timer/include \
	-I$(SDK)/src/bao1x/hardware_irq/include \
	-I$(SDK)/src/bao1x/hardware_rram/include \
	-I$(SDK)/src/bao1x/hardware_reset/include \
	-I$(SDK)/src/boards/include \
	-I$(SDK)/src/sevs

# Same flags as the SDK. Without -fno-tree-loop-distribute-patterns GCC can
# turn the SDK's memset loop into a call to memset, which recurses.
ARCH_FLAGS = -march=rv32imac_zicsr_zifencei -mabi=ilp32
AFLAGS += $(ARCH_FLAGS)
CFLAGS += $(ARCH_FLAGS) -fno-tree-loop-distribute-patterns
CFLAGS += -ffunction-sections -fdata-sections -fno-common
CFLAGS += $(INC) -Wall -Werror -std=gnu11 $(BASE_CFLAGS)

ifeq ($(DEBUG),1)
CFLAGS += -ggdb3 -Os
else
CFLAGS += -Os -g
endif

CFLAGS += -DCFG_TUSB_MCU=9100 -DCFG_TUSB_OS=OPT_OS_NONE
CFLAGS += -DCFG_TUD_CDC_RX_BUFSIZE=1024 -DCFG_TUD_CDC_TX_BUFSIZE=1024 -DCFG_TUD_MSC_BUFSIZE=512
CFLAGS += $(BAOCHIP_EXTRA_CFLAGS)
CFLAGS += -Wno-error=unused-parameter -Wno-cast-align -Wno-error=cast-align

LINKERFILE = linking/baochip.ld
LDFLAGS = $(ARCH_FLAGS) -nostartfiles -Wl,-T,$(LINKERFILE) -Wl,-Map=$@.map \
	-Wl,-cref -Wl,--gc-sections -Wl,--print-memory-usage

LIBS := -lgcc -lc
ifndef INTERNAL_LIBM
LIBS += -lm
endif

SRC_SDK = \
	$(SDK)/src/bao1x/hardware_gpio/gpio.c \
	$(SDK)/src/bao1x/hardware_uart/uart.c \
	$(SDK)/src/bao1x/hardware_i2c/i2c.c \
	$(SDK)/src/bao1x/hardware_spi/spi.c \
	$(SDK)/src/bao1x/hardware_pwm/pwm.c \
	$(SDK)/src/bao1x/hardware_adc/adc.c \
	$(SDK)/src/bao1x/hardware_trng/trng.c \
	$(SDK)/src/bao1x/hardware_sha/sha.c \
	$(SDK)/src/bao1x/hardware_sha/sha_stream.c \
	$(SDK)/src/bao1x/hardware_aes/aes.c \
	$(SDK)/src/bao1x/hardware_rram/rram.c \
	$(SDK)/src/common/bao_stdlib/delay.c \
	$(SDK)/src/common/bao_stdlib/stdio.c \
	$(SDK)/src/common/bao_stdlib/stdlib.c \
	$(SDK)/src/common/bao_stdlib/events.c \
	$(SDK)/src/common/bao_stdlib/forbidden.c \
	$(SDK)/src/sevs/sevs_assert_target.c

SDK_CFLAGS = $(ARCH_FLAGS) -Os -g -ffreestanding -fno-tree-loop-distribute-patterns \
	-ffunction-sections -fdata-sections -Wall $(INC)

SDK_O = $(addprefix $(BUILD)/sdk/, $(notdir $(SRC_SDK:.c=.o)))
SDK_O += $(BUILD)/sdk/crt0.o

$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_gpio/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_uart/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_i2c/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_spi/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_pwm/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_adc/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_trng/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_rram/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_sha/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/bao1x/hardware_aes/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/common/bao_stdlib/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/%.o: $(SDK)/src/sevs/%.c | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk/crt0.o: $(SDK)/src/runtime/crt0.S | $(BUILD)/sdk
	$(STEPECHO) "SDK $<"
	$(Q)$(CC) $(SDK_CFLAGS) -c -o $@ $<
$(BUILD)/sdk:
	$(Q)mkdir -p $@

SRC_C += \
	background.c \
	mphalport.c \
	boards/$(BOARD)/board.c \
	boards/$(BOARD)/pins.c \
	peripherals/pins.c \
	peripherals/irq.c \
	bindings/baochip/__init__.c \
	bindings/baosec/__init__.c \
	usb/corigine/dcd_corigine_udc.c \
	shared/runtime/gchelper_native.c

SRC_S += shared/runtime/gchelper_rv32i.s

# The stock MSC class stalls endpoints, which the Corigine UDC does not
# handle. The port's copy never does.
ifeq ($(CIRCUITPY_USB_MSC),1)
SRC_SUPERVISOR := $(filter-out lib/tinyusb/src/class/msc/msc_device.c,$(SRC_SUPERVISOR))
SRC_C += usb/msc_device_nostall.c
INC += -I../../lib/tinyusb/src/class/msc
endif

# aesio runs on the chip's AES engine in place of the software version.
ifeq ($(CIRCUITPY_AESIO),1)
SRC_COMMON_HAL_SHARED_MODULE_EXPANDED := $(filter-out shared-module/aesio/__init__.c shared-module/aesio/aes.c,$(SRC_COMMON_HAL_SHARED_MODULE_EXPANDED))
SRC_C += common-hal/aesio/__init__.c common-hal/aesio/engine.c
endif

OBJ += $(PY_O) $(SUPERVISOR_O) $(addprefix $(BUILD)/, $(SRC_C:.c=.o))
OBJ += $(addprefix $(BUILD)/, $(SRC_COMMON_HAL_SHARED_MODULE_EXPANDED:.c=.o))
ifeq ($(INTERNAL_LIBM),1)
OBJ += $(addprefix $(BUILD)/, $(SRC_LIBM:.c=.o))
endif
OBJ += $(addprefix $(BUILD)/, $(SRC_CIRCUITPY_COMMON:.c=.o))
OBJ += $(addprefix $(BUILD)/, $(SRC_S:.s=.o))
OBJ += $(addprefix $(BUILD)/, $(SRC_MOD:.c=.o))
OBJ += $(SDK_O)

SRC_QSTR += $(SRC_C) $(SRC_SUPERVISOR) $(SRC_CIRCUITPY_COMMON) \
	$(SRC_COMMON_HAL_SHARED_MODULE_EXPANDED) $(SRC_MOD)
SRC_QSTR_PREPROCESSOR +=

all: $(BUILD)/firmware.elf $(BUILD)/firmware.bin $(BUILD)/firmware.uf2

$(BUILD)/firmware.elf: $(OBJ) $(LINKERFILE)
	$(STEPECHO) "LINK $@"
	$(Q)echo $(OBJ) > $(BUILD)/firmware.objs
	$(Q)$(CC) -o $@ $(LDFLAGS) @$(BUILD)/firmware.objs -Wl,--start-group $(LIBS) -Wl,--end-group

$(BUILD)/firmware.bin: $(BUILD)/firmware.elf
	$(STEPECHO) "Create $@"
	$(Q)$(OBJCOPY) -O binary $^ $@

# Signed the way the SDK signs its examples.
$(BUILD)/firmware.uf2: $(BUILD)/firmware.bin
	$(STEPECHO) "Create $@"
	$(Q)$(PYTHON) $(SDK)/tools/sign_and_uf2.py $< $@ 0x60060000 0xa7d76373

audit:
	$(PYTHON) $(SDK)/tools/audit_addresses.py . ../../supervisor ../../main.c

include $(TOP)/py/mkrules.mk
