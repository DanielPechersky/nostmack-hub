import os

os.execlp(
    "podman",
    "podman",
    "run",
    "--rm",
    "--privileged",
    "--network=host",
    "--env-file",
    "/home/pi/nostmack-hub/config.env",
    "--mount",
    "type=bind,src=/home/pi/nostmack-hub/sounds,dst=/app/sounds,ro",
    "--mount",
    "type=bind,src=/home/pi/nostmack-hub/nostmack_hub,dst=/app/nostmack_hub,ro",
    "--mount",
    "type=bind,src=/var/run/dbus,dst=/var/run/dbus",
    "--mount",
    "type=bind,src=/var/run/avahi-daemon/socket,dst=/var/run/avahi-daemon/socket",
    "--log-driver=none",
    "nostmack_hub",
)
