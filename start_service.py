import subprocess
import os

hotspot_state = subprocess.run(
    "nmcli -f GENERAL.STATE con show Hotspot",
    shell=True,
    capture_output=True,
    check=True,
)

if b"activated" not in hotspot_state.stdout:
    print("Bringing up hotspot")
    subprocess.run(
        r'nmcli device wifi hotspot ssid "${SSID}" password "${PASSWORD}"',
        shell=True,
        check=True,
    )

python = "/home/pi/nostmack-hub/.venv/bin/python"
os.execlp(python, python, "-m", "nostmack_hub")
