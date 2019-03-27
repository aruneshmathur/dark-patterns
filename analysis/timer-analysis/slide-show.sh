#!/bin/bash
python add_timestamp_to_screenshots.py
cd /mnt/10tb4/dp-crawls/
mkdir -p timer-slideshow
ffmpeg -y -framerate 5  -pattern_type glob -i 'stateful_countdown_crawl_*/output/*/*marked.png' -g 1 -c:v libx264 /mnt/ssd/timer-slideshow/timer.mp4
chmod o+r /mnt/ssd/timer-slideshow/timer.mp4
scp /mnt/ssd/timer-slideshow/timer.mp4 macar@portal.cs.princeton.edu:/n/fs/darkpatterns/www/
