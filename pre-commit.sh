#!/bin/bash

./test_everything.sh
RESULT=$?
[ $RESULT -ne 0 ] && exit 1
exit 0
