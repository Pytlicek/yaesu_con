#!/usr/bin/env python3
import glob
import os
import subprocess
import sys

MODEL_ID = 1035
BAUD = 38400
LINK_PATH = "/tmp/tty.SLAB_USBtoUARTx"

ports = sorted(glob.glob("/dev/tty.SLAB_USBtoUART*")) + sorted(glob.glob("/dev/cu.SLAB_USBtoUART*"))

if not ports:
    print("Žiadne SLAB porty.")
    sys.exit(1)

found_port = None

for port in ports:
    print(f"=== Skúšam port: {port} ===")
    cmd = f"/usr/local/bin/rigctl -m {MODEL_ID} -r {port} -s {BAUD} \\ -C stop_bits=1 -C serial_handshake=None -C rts_state=OFF -C dtr_state=OFF f"
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        print("STDOUT:", res.stdout.strip())
        print("STDERR:", res.stderr.strip())
        print("Return code:", res.returncode)
        if res.returncode == 0 and res.stdout.strip().isdigit():
            found_port = port
            break
    except subprocess.TimeoutExpired:
        print("TIMEOUT")

if found_port:
    print("\n\n>  Port Found:", port)
    # Zmaž starý link a vytvor nový
    if os.path.islink(LINK_PATH) or os.path.exists(LINK_PATH):
        os.remove(LINK_PATH)
    subprocess.run(f"ln -sf {found_port} {LINK_PATH}", shell=True, check=True)
    print(f">> Symlink {LINK_PATH} -> {found_port} hotový.")
else:
    print("Rádio sa nenašlo na žiadnom porte.")
    sys.exit(2)
