# Installing CircuitPython on the Dabao from macOS or Linux

Armstrong Subero

The `DabaoCircuitPython.exe` installer is for Windows. On macOS and Linux the same job is done from a terminal with `serial_flash.py`, or by running the installer window from its Python source. Both are in the `dabao_circuitpython_installer` folder.

## What you need

1. Python 3
2. The `dabao_circuitpython_installer` folder
3. A USB data cable

## Set up once

Open a terminal in the `dabao_circuitpython_installer` folder and run:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Each time you open a new terminal, run `source venv/bin/activate` again before the commands below.

### Linux only: serial port permission

On most Linux systems a normal user cannot open serial ports until added to the serial group. On Debian, Ubuntu and Fedora:

```
sudo usermod -aG dialout $USER
```

On Arch the group is `uucp`. Log out and back in for it to take effect.

## Put the board in its loader

1. Plug the Dabao into the computer.
2. Hold PROG, tap RESET, then let go of PROG.

## Find the port

```
python3 -m serial.tools.list_ports -v
```

Look for the entry with `VID:PID=1D50:6196`. That is the Dabao loader.

On Linux the port looks like `/dev/ttyACM0`.
On macOS it looks like `/dev/cu.usbmodem1101`. Use the `cu` name.

## Try CircuitPython

This installs CircuitPython and runs it. After a RESET the board waits in its loader again.

```
python3 serial_flash.py /dev/ttyACM0 firmware/circuitpython_dabao.uf2
```

## Install permanently

This installs CircuitPython and makes the board start it on every power up.

```
python3 serial_flash.py --persistent /dev/ttyACM0 firmware/circuitpython_dabao.uf2
```

Replace `/dev/ttyACM0` with your own port in both commands.

Switching a board between the two modes changes a setting that can only be changed a limited number of times. The script reads the setting first and only changes it when it differs from what you asked for. Installing again in the same mode changes nothing.

## When it is done

The script prints `Running new firmware.` and a drive named `CIRCUITPY` appears. The board is ready for RV Circuit Studio.

## The window instead of the terminal

The installer window also runs on macOS and Linux from source:

```
python3 dabao_installer.py
```

It finds the port by itself and has the same two choices as buttons, plus Start CircuitPython for a board set up with Try.

## If something goes wrong

`boot1 is not answering`
The board is not in its loader. Hold PROG, tap RESET, let go of PROG, then run the command again.

`could not open /dev/...`
Wrong port name, or on Linux the permission step above was skipped. Close any serial monitor that has the port open.

`pyserial not installed`
The venv is not active. Run `source venv/bin/activate`.

No entry with `1D50:6196` in the port list
Try another cable. Many USB cables carry power only.

To flash a board again after Install Permanently, hold PROG through reset as above. That always returns the board to its loader.
