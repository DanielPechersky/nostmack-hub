# Nostalgia Machina Hub

This code runs on the Raspberry Pi that coordinates the whole exhibit. It is notified when a gear is turned. In response, it:
1. controls WLED
2. plays sounds

Additionally, this codebase contains a preview that simulates the machine.

## Setup

The hub and the preview require configuration through an env file, as well as a directory full of sounds to play.

Example env file:
```
SSID=
PASSWORD=

WLED_ADDRESS=wled.local
LED_COUNT=840
GEARS=0:5,1:5,2:5,3:5,4:5

SOUND_POOL=sounds/pool
SOUND_DING=sounds/ding.wav
SOUND_FINALE=sounds/finale.wav
```

Example sound layout:
```
sounds/pool/sound{1..5}.wav
sounds/ding.wav
sounds/finale.wav
```
