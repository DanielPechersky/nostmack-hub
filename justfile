monitor:
    ssh nostmack-pi 'journalctl -f -u nostmack-hub'

ssh:
   ssh nostmack-pi

disable_hotspot: (systemctl "disable")
    ssh nostmack-pi 'sudo reboot'

deploy_code: && (systemctl "restart")
    #!/usr/bin/env bash

    set -e

    docker build -t nostmack_hub .

    docker save -o nostmack_hub.tar nostmack_hub

    install_dir=$(ssh nostmack-pi mktemp -d)
    rsync --progress nostmack_hub.tar "nostmack-pi:${install_dir}"

    ssh nostmack-pi sudo docker load --input "${install_dir}/nostmack_hub.tar"

    ssh nostmack-pi rm -rf "${install_dir}"

deploy_env:
    rsync config.env nostmack-pi:/home/pi/nostmack-hub/

deploy_service: && daemon_reload (systemctl "restart")
    rsync start_service.py nostmack-pi:/home/pi/nostmack-hub
    rsync nostmack-hub.service nostmack-pi:/home/pi/
    ssh nostmack-pi 'sudo mv /home/pi/nostmack-hub.service /etc/systemd/system/nostmack-hub.service'

deploy_sounds:
    rsync --delete --exclude=.DS_Store -r sounds nostmack-pi:/home/pi/nostmack-hub/

daemon_reload:
    ssh nostmack-pi 'sudo systemctl daemon-reload'

systemctl command:
    ssh nostmack-pi 'sudo systemctl {{ command }} nostmack-hub'

test:
   poetry run pytest
