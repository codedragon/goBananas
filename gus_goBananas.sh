#!/bin/bash
cp gus_config.py config.py
#ppython goBananas.py -sGus --no-eeg --resolution=1024x768
SD=( data/Gus/session_$(date +%y_%m_%d) )
TEST=
#BD=/r/"Buffalo Lab"/"VR Task Data UW"/Giuseppe/"panda data"/
BD=( /r/Buffalo\ Lab/VR\ Task\ Data\ UW/Giuseppe/panda\ data/JN_$(date +%y_%m_%d)* )
ND=( /r/Buffalo\ Lab/VR\ Task\ Data\ UW/Giuseppe/panda\ data/JN_$(date +%y_%m_%d)* )
echo "from directory"
echo "${SD}"
ls "${SD}"
echo "to directory"
echo "${BD}"
#mkdir "${BD}"
#ls "${BD}"
#cp -r $SD "${BD}"
#echo "copied directory"
#ls $SD
#ls "${BD}"
EFILE=( ../calibrate/data/Gus/eye_cal2_$(date +%y_%m_%d)* )
TFILE=( ../calibrate/data/Gus/time_cal2_$(date +%y_%m_%d)* )
# will only save to first data directory of that day.
if [ -a "${EFILE}" ]
then
    echo "yup" 
    #cp -r $EFILE "${ND}"
fi
if [ -a "${TFILE}" ]
then
    echo "yup" 
    #cp -r $TFILE "${ND}"
fi

