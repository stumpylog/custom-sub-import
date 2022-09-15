# custom-sub-import

A toolbox for importing subtitles from grabbed media for Radarr and Sonarr.  It locates subtitles
alongside downloaded items, and copies them to nicely named files in the destination.

Currently, it only supports SRT file and English subtitles for RARBG and VXT release groups.
Within that set, it will attempt to locate normal, forced and SDH subtitles, based on the number
of files found and the various sizes.

## Installation

1. Place 01-install-python.sh into `/custom-cont-init.d/` of your container (see the LinuxServer.io [blog post](https://www.linuxserver.io/blog/2019-09-14-customizing-our-containers) for details)
2. Place `custom-sub-import.py` and `locate.py`  somewhere accessible in the container such as `/config/scripts`
3. Under Settings -> Connect, add as a custom script for "On Import" and "On Upgrade"

Mostly setup for use with the LinuxServer.io containers, but should would or be adaptable for other setups.
