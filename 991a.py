#!/usr/bin/env python3
import glob
import os
import subprocess
import sys
import shutil

MODEL_ID = 1035
BAUD = 38400
LINK_PATH = "/tmp/tty.SLAB_USBtoUARTx"
RIGCTL = shutil.which("rigctl") or "/usr/local/bin/rigctl"

def run_rigctl_one_liner(port: str, timeout_sec: int = 5) -> tuple[bool, str, str, int]:
    cmd = f'{RIGCTL} -m {MODEL_ID} -r {port} -s {BAUD} \\ -C stop_bits=1 -C serial_handshake=None -C rts_state=OFF -C dtr_state=OFF f'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout_sec)
    ok = (res.returncode == 0 and res.stdout.strip().isdigit())
    return ok, res.stdout.strip(), res.stderr.strip(), res.returncode

def current_link_target() -> str | None:
    if os.path.islink(LINK_PATH):
        return os.path.realpath(LINK_PATH)
    return None

def ensure_parent_dir(path: str):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def main():
    # 1) Check existing link
    tgt = current_link_target()
    if tgt and os.path.exists(tgt):
        print(f"Checking existing link: {LINK_PATH} -> {tgt}")
        try:
            ok, out, err, rc = run_rigctl_one_liner(tgt, timeout_sec=5)
            print("STDOUT:", out)
            if err: print("STDERR:", err)
            print("Return code:", rc)
            if ok:
                print("Existing link works. No action needed.")
                sys.exit(0)
            else:
                print("Existing link does not reply. Finding new port…")
        except subprocess.TimeoutExpired:
            print("TIMEOUT when using existing link. Finding new port…")
    else:
        if tgt:
            print(f"Link {LINK_PATH} -> {tgt}, but target does not exist. Finding new port…")
        else:
            print("Link does not exist. Finding new port…")

    # 2) iterate over ports and find one that works
    ports = sorted(glob.glob("/dev/tty.SLAB_USBtoUART*")) + sorted(glob.glob("/dev/cu.SLAB_USBtoUART*"))
    if not ports:
        print("No SLAB ports.")
        sys.exit(1)

    found_port = None
    for port in ports:
        print(f"=== Trying port: {port} ===")
        try:
            ok, out, err, rc = run_rigctl_one_liner(port, timeout_sec=5)
            print("STDOUT:", out)
            # if err: print("STDERR:", err)
            print("Return code:", rc)
            if ok:
                found_port = port
                break
        except subprocess.TimeoutExpired:
            print("TIMEOUT")

    if not found_port:
        print("TRX not found on any port.")
        sys.exit(2)

    # 3) create symlink in /tmp
    ensure_parent_dir(LINK_PATH)
    if os.path.islink(LINK_PATH) or os.path.exists(LINK_PATH):
        try:
            os.remove(LINK_PATH)
        except Exception as e:
            print(f"Unable to remove {LINK_PATH}: {e}")
            sys.exit(3)

    cmd_ln = f"ln -sf {found_port} {LINK_PATH}"
    subprocess.run(cmd_ln, shell=True, check=True)
    print(f">> Symlink {LINK_PATH} -> {found_port} done.")

if __name__ == "__main__":
    main()
