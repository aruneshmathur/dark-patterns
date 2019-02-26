#!/bin/bash
cd ~
mkdir -p timer-slideshow
ffmpeg -framerate 5  -pattern_type glob -i 'stateful_countdown_crawl_*/output/*/*marked.png' -g 1 -c:v libx264 ~/timer-slideshow/timer.mp4
