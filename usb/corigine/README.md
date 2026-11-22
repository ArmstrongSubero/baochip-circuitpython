# Corigine UDC driver

TinyUSB device driver for the Corigine UDC in the Baochip-1x, written by Andrew Leech and the MicroPython contributors. MIT licensed.

Source: `github.com/andrewleech/tinyusb`, branch `corigine-udc`, commit `d7d3694c`, folder `src/portable/corigine/udc`.

That branch is TinyUSB 0.19. CircuitPython carries TinyUSB 0.21, where `dcd_edpt_xfer` takes a fifth argument, `is_isr`. Two lines of `dcd_corigine_udc.c` were changed for that: the function's signature and its one internal call. Nothing else differs from the source.
