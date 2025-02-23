import os

os.execlp(
    "podman",
    "podman",
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
    "--log-driver=none",
    "nostmack_hub",
)
