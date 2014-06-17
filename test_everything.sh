#!/bin/bash

arch=$(uname -m)
OUTPUT="A test has failed, please troubleshoot test suite "
if [ "$arch" == 'x86_64' ]
then
    for i in {0..3}; do
        arch -i386 ppython test_trainingBananas.py $i &> /dev/null || { echo $OUTPUT $i; exit 1;}
    done
else
    #ppython test_trainingBananas.py 1 &> /dev/null || { echo hello; exit 1; }
    echo do some tests
    for i in {0..3}; do
        echo $i
        ppython test_trainingBananas.py $i &> /dev/null || { echo $OUTPUT $i; exit 1; }
        echo yup
    done
fi
#ppython test_moBananas.py &> /dev/null || echo A test in moBananas failed && exit 1

