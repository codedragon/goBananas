#!/bin/bash
# make sure we are using the correct configuration
cp configs/mp_goB_config.py config.py
ppython goBananas.py -sMP --no-eeg --resolution=1280x800
# original directory
SD=( data/MP/session_$(date +%y_%m_%d)* )

# change to better name
DATESTR=${SD:16:14}
#echo $DATESTR
SND=( data/MP/MP_$DATESTR )
mv $SD "${SND}"

# make copy to research backup drive
BD=/r/"Buffalo Lab"/"VR Task Data UW"/MrPeepers/"panda data"/
cp -r $SND "${BD}"

# also copy calibration files, if they exist
ND=( /r/Buffalo\ Lab/VR\ Task\ Data\ UW/MrPeepers/panda\ data/MP_$(date +%y_%m_%d)*/ )
#echo $ND
EFILE=( ../calibrate/data/MP/eye_cal2_$(date +%y_%m_%d)* )
TFILE=( ../calibrate/data/MP/time_cal2_$(date +%y_%m_%d)* )
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
