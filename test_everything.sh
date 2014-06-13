#!/bin/bash

arch=$(uname -m)
if [ "$arch" == 'x86_64' ]
then
    arch -i386 ppython test_trainingBananas.py TrainingBananaTestsT2 2>&1 /dev/null
    arch -i386 ppython test_trainingBananas.py TrainingBananaTestsT2_1 2>&1 /dev/null
    arch -i386 ppython test_trainingBananas.py TrainingBananaTestsT2_2 2>&1 /dev/null
    arch -i386 ppython test_trainingBananas.py TrainingBananaTestKeys 2>&1 /dev/null
else
    echo "one"
    #ppython test_trainingBananas.py 0 &> /dev/null || exit 1 
    #ppython test_trainingBananas.py TrainingBananaTestsT2 &> /dev/null || exit 1
    #ppython test_trainingBananas.py TrainingBananaTestsT2_1 2>&1 /dev/null || exit 1
    #ppython test_trainingBananas.py TrainingBananaTestsT2_2 &> /dev/null || exit 1
    #echo $?
    echo "two"
    #ppython test_trainingBananas.py 1 &> /dev/null || exit 1 
    #ppython test_trainingBananas.py TrainingBananaTestKeys &> /dev/null || exit 1
    #echo $?
fi
echo "three"
ppython test_moBananas.py &> /dev/null || exit 1
echo $?
