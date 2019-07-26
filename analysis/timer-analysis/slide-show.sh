#!/bin/bash
python add_timestamp_to_screenshots.py
CRAWL_DIR=''  # set to crawl data directory
cd $CRAWL_DIR
mkdir -p timer-slideshow
ffmpeg -y -framerate 5  -pattern_type glob -i 'stateful_countdown_crawl_*/output/*/*marked.png' -g 1 -c:v libx264 timer.mp4
# chmod o+r timer.mp4
# scp SRC DST
