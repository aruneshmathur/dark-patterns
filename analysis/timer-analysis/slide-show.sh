#!/bin/bash
python add_timestamp_to_screenshots.py
cd ~
mkdir -p timer-slideshow
ffmpeg -y -framerate 5  -pattern_type glob -i 'stateful_countdown_crawl_*/output/*/*marked.png' -g 1 -c:v libx264 ~/timer-slideshow/timer.mp4
