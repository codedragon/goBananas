#!/bin/bash
cp mp_config.py config.py
#ppython trainBananas.py -sTest --no-eeg --resolution=1024x768
ppython trainBananas.py -sMP --no-eeg --js-zero-threshold=0.05 --resolution=1024x768
#arch -i386 ppython trainBananas.py -sTest --no-eeg --no-fs
echo "Thanks for playing."
