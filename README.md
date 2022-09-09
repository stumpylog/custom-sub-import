# custom-sub-import

A toolbox for importing subtitles from grabbed media for Radarr and Sonarr

## Installation

1. Place 01-install-python.sh into `/config/custom-cont-init.d/` of your container
2. Place `custom-sub-import.py` somewhere accessible in the container such as `/config/scripts`
3. Under Settings -> Connect, add as a custom script for "On Import" and "On Upgrade"

Mostly setup for use with the LinuxServer.io containers, but should would or be adaptable for other setups.
