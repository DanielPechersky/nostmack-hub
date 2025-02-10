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

os.execlp(
    "docker",
    "docker",
    "run",
    "--privileged",
    "--env-file",
    "/home/pi/nostmack-hub/config.env",
    "--mount",
    "type=bind,src=/home/pi/nostmack-hub/sounds,dst=/app/sounds,ro",
    "--network=host",
    "nostmack_hub",
)
