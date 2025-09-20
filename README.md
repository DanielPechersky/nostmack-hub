# Nostalgia Machina Hub

This code runs on the Raspberry Pi that coordinates the whole exhibit. It is notified when a gear is turned. In response, it:
1. controls WLED
2. plays sounds

Additionally, this codebase contains a preview that simulates the machine.

## Setup

The hub and the preview require configuration through an env file, as well as a directory full of sounds to play.

Example env file:
```
WLED_ADDRESS=wled.local
LED_COUNT=840
GEARS=0:5,1:5,2:5,3:5,4:5
COLOURS=[[37, 255, 90], [255, 0, 0], [0, 255, 255], [255, 80, 0], [180, 0, 255]]
FINALE_DURATION=50

ALSA_CARD=Headphones

SOUND_POOL=sounds/pool
SOUND_DING=sounds/ding.ogg
SOUND_FINALE=sounds/finale.ogg
```

Example sound layout:
```
sounds/pool/sound{1..5}.ogg
sounds/ding.ogg
sounds/finale.ogg
```
