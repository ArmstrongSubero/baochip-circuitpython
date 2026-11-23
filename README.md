# CircuitPython for the Dabao (Baochip-1x)

Armstrong Subero

A CircuitPython port for the Dabao board. The REPL runs on the board's own USB port, CIRCUITPY shows up as a USB drive, and the header pins work through the standard `digitalio`, `busio`, `pwmio` and `analogio` modules. SHA, HMAC and AES run on the chip's crypto hardware.

This folder is `ports/baochip` of a CircuitPython tree. Nothing outside it is modified.

Status is beta. Built on CircuitPython 11.0.0 alpha 3 (commit `b2680c85d4`). Tested on Dabao hardware. 

The port provides 1.45MB for heap for python and storage is 512KB for files. 

For Windows installation download and run the windows installer from the releases and follow the guide in this repository. MAC and Linux users can use thier guide. 



It is HIGHLY Recommended to download Rovari CircuitStudio to use this port. CircuitStudio allows the Baochip to save to SRAM without any wear on the internal RRAM and will prolong the life of your device. 



## What works

| Module              | Pins                         | Notes                                                       |
| ------------------- | ---------------------------- | ----------------------------------------------------------- |
| `digitalio`         | all header pins              | Pull ups only. The chip has no pull downs.                  |
| `busio.I2C`         | SCL PB11, SDA PB12           | I2C0, 1 kHz to 1 MHz, internal pull ups on                  |
| `busio.SPI`         | SCK PC0, MOSI PC1, MISO PC2  | SPI2, 8 bit, 193 kHz and up. Chip select is any GPIO.       |
| `busio.UART`        | TX PB14, RX PB13             | UART2, 8N1                                                  |
| `pwmio.PWMOut`      | PB1 PB2 PB3, PC0 PC1 PC2 PC3 | Pins in the same group share a frequency                    |
| `analogio.AnalogIn` | PC9 (`board.A0`)             | 10 bit, accurate from 0.3 V to 1.0 V                        |
| `hashlib`           |                              | SHA256 and SHA512 on the hash engine                        |
| `aesio`             |                              | AES ECB, CBC and CTR on the AES engine, 128 to 256 bit keys |
| `baosec`            |                              | `hmac_sha256`, `hmac_sha512`, `compare`                     |
| `os.urandom`        |                              | True random number generator                                |

Also built in: `microcontroller`, `storage`, `supervisor`, `usb_cdc`, `time`, `random`, `math`, `struct`, `json`, `re`, `binascii`, `collections`, `array`, `io`, `errno`, `zlib`, `traceback`

The frozen libraries supported are: `asyncio`, `adafruit_ticks`, `adafruit_register`, `adafruit_bus_device`, `simpleio` and `adafruit_motor`.



I should note that PC13 (PROG) is not available to programs. It shorts the USB data lines when low and the USB driver uses it to disconnect from the bus.



## Saving files

The Baochip's RRAM is rated for about 10,000 write cycles, so CIRCUITPY lives in RAM. Copying a file to the drive costs nothing, but it is gone after a reset unless you save it to the chip:

```python
import baochip
baochip.pending()   # pages that differ from the saved copy
baochip.save()      # write those pages to RRAM
```

`save()` writes only the 32 byte pages that changed. When `pending()` returns 0, everything is saved.

If a save is interrupted by a reset or power loss, the files that were being changed can be left part written. Files that were not changed are not affected. In RV CircuitStudio, press "Save Permanently". In other editors do this: 

```markdown
    import baochip
    baochip.save()
```



## Security

```python
import hashlib, aesio, baosec

digest = hashlib.new("sha256", b"hello").digest()
mac = baosec.hmac_sha256(b"key", b"message")

out = bytearray(16)
aesio.AES(bytes(16), aesio.MODE_ECB).encrypt_into(b"sixteen byte msg", out)
```

`hashlib` and `aesio` are the standard CircuitPython modules, so code written for other boards runs unchanged. None of this is hardened against side channels.



## Testing

`tests/full_test_code.py` runs 200 checks covering the pins, the software modules and the crypto. It needs four jumpers and nothing else:

| Jumper       | Tests                |
| ------------ | -------------------- |
| PB1 to PB4   | `digitalio`, `pwmio` |
| PB14 to PB13 | `busio.UART`         |
| PC1 to PC2   | `busio.SPI`          |
| PC8 to PC9   | `analogio`           |

Leave PB11 and PB12 empty, copy the file to CIRCUITPY as `code.py`, and it prints a result for each section and `RESULT: PASS` at the end.

The port also runs in baoemu, the emulator in the SDK:

```
baoemu --usb-console build-dabao/firmware.elf
```

## Build options

| Option                                                           | Effect                                       |
| ---------------------------------------------------------------- | -------------------------------------------- |
| `BAOCHIP_UART_CONSOLE=1`                                         | Adds a REPL on UART2 at 115200, for bring up |
| `CIRCUITPY_USB_DEVICE=0 CIRCUITPY_USB_CDC=0 CIRCUITPY_USB_MSC=0` | No USB, REPL on UART2 only                   |

## Limits

* One I2C, one SPI and one UART, on the pins above.
* `time.sleep` is a busy wait.
* The board does not support`AnalogOut`, `neopixel_write`, `displayio`, `rtc` or `usb_hid`.
* If the firmware crashes it prints a trap report on PB14 at 115200 and halts.

## Credits

USB runs on CircuitPython's TinyUSB with the Corigine UDC driver by Andrew Leech and the MicroPython contributors (`usb/corigine`). The interrupt dispatch in `peripherals/irq.c` is adapted from the same MicroPython port. `usb/msc_device_nostall.c` is TinyUSB's mass storage class with endpoint stalls were removed.

## License

MIT.
