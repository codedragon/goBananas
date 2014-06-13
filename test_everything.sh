#!/bin/bash

arch=$(uname -m)
if [ "$arch" == 'x86_64' ]
then
    arch -i386 ppython test_trainingBananas.py TrainingBananaTestsT2 > /dev/null
    arch -i386 ppython test_trainingBananas.py TrainingBananaTestsT2_1 > /dev/null
    arch -i386 ppython test_trainingBananas.py TrainingBananaTestsT2_2 > /dev/null
    arch -i386 ppython test_trainingBananas.py TrainingBananaTestKeys > /dev/null
else
    ppython test_trainingBananas.py TrainingBananaTestsT2 > /dev/null
    ppython test_trainingBananas.py TrainingBananaTestsT2_1 > /dev/null
    ppython test_trainingBananas.py TrainingBananaTestsT2_2 > /dev/null
    ppython test_trainingBananas.py TrainingBananaTestKeys > /dev/null
fi
ppython test_moBananas.py
