#!/bin/bash
cp testing_config.py config.py
# for testint peepers config
#cp mp_config.py config.py
rm -r data/Test/*
#ppython trainBananas.py -sTest --no-eeg --resolution=1024x768
#ppython trainBananas.py -sTest --no-eeg --js-zero-threshold=0.2 --resolution=1024x768
ppython trainBananas.py -sTest --no-eeg --no-fs
#ppython trainBananas.py -sTest --no-eeg --no-fs
#arch -i386 ppython trainBananas.py -sTest --no-eeg --no-fs
echo "Thanks for playing."
