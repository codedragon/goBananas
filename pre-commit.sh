#!/bin/bash

./test_everything.sh
RESULT=$?
echo $RESULT
[ $RESULT -ne 0 ] && exit 1
exit 0
