import os

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
    "--mount",
    "type=bind,src=/run/systemd,dst=/run/systemd",
    "--mount",
    "type=bind,src=/etc/systemd,dst=/etc/systemd",
    "nostmack_hub",
)
