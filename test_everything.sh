#!/bin/bash

arch=$(uname -m)
OUTPUT="A test has failed, please troubleshoot test suite "
# can change &> to > to see test output. We are printing lots to the console
# so we can see stuff during training, so getting rid of the /dev/null dump entirely
# will produce copious amounts of output.
if [ "$arch" == 'x86_64' ]
then
    for i in {0..7}; do
        echo $i
        arch -i386 ppython test_trainingBananas.py $i > /dev/null || { echo $OUTPUT $i; exit 1;}
        #echo test over
    done
    arch -i386 ppython test_moBananas.py &> /dev/null || { echo A test in moBananas failed; exit 1; }
else
    for i in {0..7}; do
        echo $i
        ppython test_trainingBananas.py $i > /dev/null || { echo $OUTPUT $i; exit 1; }
    done
    ppython test_moBananas.py &> /dev/null || { echo A test in moBananas failed; exit 1; }
fi


