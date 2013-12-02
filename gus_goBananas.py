import os
import shutil
import datetime

# make sure using correct config
shutil.copy('gus_config.py', 'config.py')
#shutil.copy('testing_config.py', 'config.py')
# get the date - will backup all sessions done today
session = "data/Gus/session_" + datetime.datetime.now().strftime("%y_%m_%d") + "*"
#session = "data/Test/session_" + datetime.datetime.now().strftime("%y_%m_%d") + "*"
# start the task
os.system('ppython goBananas.py -sGus --no-eeg --resolution=1024x768')
#os.system('ppython goBananas.py -sTest --no-eeg --resolution=1024x768')
# copy the data
# copy_this = 'cp -r ' + session + ' /r/Buffalo\\ Lab/VR\\ Task\\ Data\\ \\(uw\\)/Giuseppe/panda\\ data/'
copy_this = 'cp -r ' + session + ' /r/"Buffalo Lab"/"VR Task Data UW"/Giuseppe/"panda data"/'
#copy_this = 'cp -r ' + session + ' /r/"Buffalo Lab"/"VR Task Data UW"/Test/'
os.system(copy_this)
print 'Thanks for playing'