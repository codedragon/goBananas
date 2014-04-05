#!/bin/bash
# make sure we are using the correct configuration
cp giz_config.py config.py
ppython goBananas.py -sGus --no-eeg --resolution=1024x768
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
