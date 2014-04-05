#!/bin/bash
cp testing_config.py config.py
ppython trainBananas.py -sTest --no-eeg --js-zero-threshold=0.03 --resolution=1024x768
echo "Thanks for playing."
