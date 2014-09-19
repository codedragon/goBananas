#!/bin/bash
# set the name of the movie
MOVIE=( data/Test/test_$(date +%y_%m_%d_%H_%M).mp4 )
# take some video
#/c/ffmpeg/bin/ffmpeg -f dshow -video_size 640x480 -framerate 15 -pixel_format yuv420p -i video="Logitech QuickCam S5500" test.avi
/c/ffmpeg/bin/ffmpeg -f dshow -video_size 640x480 -framerate 30 -t 30 -pixel_format yuv420p -i video="Logitech QuickCam S5500":audio="Microphone (Logitech Mic (Quick" $MOVIE &> test.out & ppython goBananas.py -sTest --no-eeg --resolution=1280x800
#ppython goBananas.py -sTest --no-eeg --resolution=1280x800
