# Yaesu FT-991A Symlink Helper

This Python script automatically creates and maintains a stable symlink to the USB–UART device  
(Silicon Labs CP210x, `tty.SLAB_USBtoUART`) for use with [Hamlib](https://hamlib.github.io/) (`rigctl`).

The goal is to provide a consistent serial port path for applications connecting to a Yaesu FT-991A,  
regardless of which `/dev/tty.SLAB_USBtoUART*` device node the OS assigns after reconnecting the radio.

## Features

- Scans for available `/dev/tty.SLAB_USBtoUART*` and `/dev/cu.SLAB_USBtoUART*` ports  
- Tests each port using `rigctl` (`hamlib`) with the `f` (frequency) command  
- If a working port is found, creates a symlink (`/tmp/tty.SLAB_USBtoUARTx`) pointing to the correct device  
- If an existing symlink works, no changes are made  
- If the linked port stops responding, the script searches for a new one and updates the symlink  

## Requirements

- Python 3.10+  
- [Hamlib](https://hamlib.github.io/) installed (`rigctl` available in PATH)  
- OS: macOS / Linux  
- Radio: Yaesu FT-991A (Hamlib model ID `1035`)  

## Installation

Clone the repository and make the script executable:

```bash
git clone https://github.com/<your_repo>/yaesu_symlink_helper.git
cd yaesu_symlink_helper
chmod +x 991a.py
````

## Usage

Run manually:

```bash
./991a.py
```

The result will be a symlink created (or maintained):

```
/tmp/tty.SLAB_USBtoUARTx -> /dev/tty.SLAB_USBtoUART
```

### Cron job example

It is recommended to run the script periodically (e.g. once per minute) to ensure the symlink is always valid.
Add this to your crontab (`crontab -e`):

```
* * * * * /Users/tomas/Development/Python_Tools/yaesu_con/991a.py > /var/log/flrig_991a.log 2>&1
```

This will check the port every minute and refresh the symlink if necessary.

## Notes

* The symlink is created in `/tmp`, which is cleared on reboot. The cron job will recreate it automatically.
* On macOS, applications often work better with `/dev/cu.*` ports than with `/dev/tty.*`. The script tests both and uses whichever responds.
* If you prefer a different symlink path (e.g. `/usr/local/dev/tty.SLAB_USBtoUARTx`) or need a different Hamlib model ID, adjust the constants in the script header.
* On MacOS: `brew install autoconf automake pkg-config libev libfuse libusb` `brew install hamlib` or `brew update && brew upgrade hamlib`

---

⚡ If you don’t want to rely on cron, you can set up a persistent service:

* `systemd` service on Linux
* `launchd` plist on macOS
  so the symlink is automatically maintained in the background.

```
