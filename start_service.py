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

subprocess.run(
    'nmcli connection modify "Wired connection 1" ipv4.addresses 10.10.10.0/24 ipv4.method shared ipv4.routes 10.10.10.0/24 && nmcli device reapply eth0',
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
    "--mount",
    "type=bind,src=/home/pi/nostmack-hub/nostmack_hub,dst=/app/nostmack_hub,ro",
    "--network=host",
    "-v",
    "/var/run/dbus:/var/run/dbus",
    "-v",
    "/var/run/avahi-daemon/socket:/var/run/avahi-daemon/socket",
    "nostmack_hub",
)
