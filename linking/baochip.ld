/*
 * baochip.ld: CircuitPython on the Baochip-1x
 *
 * Copyright (c) 2026 Armstrong Subero
 * SPDX-License-Identifier: MIT
 *
 * Derived from the Dabao SDK's bao1x.ld. The memory map, the region
 * bounds and every build check are kept. What changes is the SRAM layout:
 * the main stack grows to 32 KB for the VM, and the space between .bss and
 * the crash record becomes the CircuitPython heap.
 *
 *   0x60000000  boot0            128 KB   immutable, write locked
 *   0x60020000  boot1            256 KB   signed, never written by us
 *   0x60060000  program          1 MB     this image
 *   0x60160000  runtime storage           rram_write() at run time
 *   0x603DA000  one-way counters          security, never touch
 *   0x603E0000  data slots                security, never touch
 *
 *   0x61000000  SRAM             2 MB     .data, .bss, heap, stacks
 *   0x50000000  IFRAM0           128 KB   DMA buffers, top 4 KB reserved
 *   0x50020000  IFRAM1           128 KB   DMA buffers
 */

ENTRY(_start)

MEMORY
{
    SIGBLOCK (r)  : ORIGIN = 0x60060000, LENGTH = 0x300
    RRAM (rx)     : ORIGIN = 0x60060300, LENGTH = 0xFFD00
    SRAM (rwx)    : ORIGIN = 0x61000000, LENGTH = 0x200000
    IFRAM0 (rw)   : ORIGIN = 0x50000000, LENGTH = 0x1F000
    IFRAM1 (rw)   : ORIGIN = 0x50020000, LENGTH = 0x20000
}

_program_start   = 0x60060000;
_program_end     = 0x60160000;
_boot1_start     = 0x60020000;

_trap_stack_size = 0x2000;
_stack_size      = 0x8000;
_stack_top       = ORIGIN(SRAM) + LENGTH(SRAM);
_trap_stack_top  = _stack_top;
_main_stack_top  = _trap_stack_top - _trap_stack_size;
_stack_limit     = _main_stack_top - _stack_size;

_sevs_crash_size  = 0x100;
_sevs_crash_start = _stack_limit - _sevs_crash_size;

/* One word below the crash record that crt0.S never zeroes, for the safe
 * mode flag that has to survive a soft reset. */
_saved_word = _sevs_crash_start - 0x10;

SECTIONS
{
    .text : ALIGN(4)
    {
        *(.text.start)
        *(.text .text.*)
        *(.rodata .rodata.*)
        *(.srodata .srodata.*)
        *(.gnu.linkonce.r.*)
        . = ALIGN(4);
    } > RRAM

    .preinit_array : ALIGN(4)
    {
        PROVIDE_HIDDEN(__preinit_array_start = .);
        KEEP(*(.preinit_array*))
        PROVIDE_HIDDEN(__preinit_array_end = .);
    } > RRAM

    .init_array : ALIGN(4)
    {
        PROVIDE_HIDDEN(__init_array_start = .);
        KEEP(*(SORT(.init_array.*)))
        KEEP(*(.init_array*))
        PROVIDE_HIDDEN(__init_array_end = .);
    } > RRAM

    .fini_array : ALIGN(4)
    {
        PROVIDE_HIDDEN(__fini_array_start = .);
        KEEP(*(SORT(.fini_array.*)))
        KEEP(*(.fini_array*))
        PROVIDE_HIDDEN(__fini_array_end = .);
    } > RRAM

    .data : ALIGN(4)
    {
        _data_start = .;
        *(.data .data.*)
        *(.sdata .sdata.*)
        . = ALIGN(4);
        _data_end = .;
    } > SRAM AT > RRAM

    _data_lma   = LOADADDR(.data);
    _image_end  = _data_lma + (_data_end - _data_start);
    _image_size = _image_end - _program_start;

    .bss (NOLOAD) : ALIGN(4)
    {
        _bss_start = .;
        *(.bss .bss.*)
        *(.sbss .sbss.*)
        *(COMMON)
        . = ALIGN(4);
        _bss_end = .;
    } > SRAM

    _heap_start = ALIGN(_bss_end, 16);
    _heap_end   = _saved_word & ~0xF;

    .sevs_crash _sevs_crash_start (NOLOAD) :
    {
        KEEP(*(.sevs_crash))
        . = _sevs_crash_size;
    } > SRAM

    .stack _stack_limit (NOLOAD) :
    {
        _stack_bottom = .;
        . = . + _stack_size + _trap_stack_size;
    } > SRAM

    .dma_buffers (NOLOAD) : ALIGN(4)
    {
        _dma_start = .;
        *(.dma_buffers .dma_buffers.*)
        . = ALIGN(4);
        _dma_end = .;
    } > IFRAM0

    __global_pointer$ = _data_start + 0x800;

    /DISCARD/ :
    {
        *(.comment)
        *(.note.*)
        *(.eh_frame*)
    }

    ASSERT(_image_end <= _program_end,
        "Program too large: the image runs past 0x60160000 into runtime storage.")
    ASSERT(ADDR(.text) >= _program_start,
        "Code is placed below 0x60060000, which is the boot0 and boot1 region.")
    ASSERT(_data_lma >= _program_start,
        "Initialised data is placed below 0x60060000, which is the boot0 and boot1 region.")
    ASSERT(_bss_end <= _sevs_crash_start,
        "Out of SRAM: .bss reaches the crash record and stack at the top of memory.")
    ASSERT(_heap_end - _heap_start >= 0x40000,
        "Heap under 256 KB: .bss has grown too large.")
    ASSERT(_stack_limit + _stack_size + _trap_stack_size == _stack_top,
        "Stack reservation does not reach the top of SRAM.")
    ASSERT(_trap_stack_size >= 0x400,
        "Trap stack too small. Keep _trap_stack_size at 0x400 or more.")
    ASSERT(_dma_end <= ORIGIN(IFRAM0) + LENGTH(IFRAM0),
        "Too many DMA buffers: .dma_buffers reaches 0x5001F000, the boot chain UART buffer.")
}
