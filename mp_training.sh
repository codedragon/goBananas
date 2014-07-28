#!/bin/bash
# make sure we are using the correct configuration
cp configs/mp_config.py train_config.py
ppython trainingBananas.py
