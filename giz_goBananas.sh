#!/bin/bash
# set the name of the movie
MOVIE=( data/Gus/JN_$(date +%y_%m_%d_%H_%M).mp4)

# make sure we are using the correct configuration
cp configs/giz_config.py config.py

# take some video and start the task
/c/ffmpeg/bin/ffmpeg -f dshow -video_size 640x480 -framerate 30 -t 180 -pixel_format yuv420p -i video="Logitech QuickCam S5500":audio="Microphone (Logitech Mic (Quick" $MOVIE &> test.out & ppython goBananas.py -sGus --no-eeg --resolution=1280x800
#ppython goBananas.py -sGus --no-eeg --resolution=1280x800

# original directory
SD=( data/Gus/session_$(date +%y_%m_%d)* )

# change to better name
DATESTR=${SD:17:14}
#echo $DATESTR
SND=( data/Gus/JN_$DATESTR )
mv $SD "${SND}"

# make copy to research backup drive
BD=/r/"Buffalo Lab"/"VR Task Data UW"/Giuseppe/"panda data"/
cp -r $SND "${BD}"

# also copy calibration files, if they exist
ND=( /r/Buffalo\ Lab/VR\ Task\ Data\ UW/Giuseppe/panda\ data/JN_$(date +%y_%m_%d)*/ )
#echo $ND
EFILE=( ../calibrate/data/Gus/eye_cal2_$(date +%y_%m_%d)* )
TFILE=( ../calibrate/data/Gus/time_cal2_$(date +%y_%m_%d)* )
# will only save to first data directory of that day.
if [ -a "${EFILE}" ]
then
    #echo "yup" 
    cp -r $EFILE "${ND}"
fi
if [ -a "${TFILE}" ]
then
    #echo "yup" 
    cp -r $TFILE "${ND}"
fi
echo "Thanks for playing."
