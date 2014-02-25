import os
import shutil
import datetime

# make sure using correct config
#shutil.copy('gus_config.py', 'config.py')
shutil.copy('testing_config.py', 'config.py')
# get the date - will backup all sessions done today
today_str = datetime.datetime.now().strftime("%y_%m_%d") + "*"
#session = "data/Gus/JN_" + today_str
session = "data/Test/JN_" + today_str
# start the task
#os.system('ppython goBananas.py -sGus --no-eeg --resolution=1024x768')
os.system('ppython goBananas.py -sTest --no-eeg --resolution=1024x768')
# copy the data
backup_dir = ' /r/"Buffalo Lab"/"VR Task Data UW"/Giuseppe/"panda data"/'
# get name of directory we just created
copy_this = 'cp -r ' + session + backup_dir
print('gobananas', copy_this)
os.system(copy_this)
# if there are calibration files for today, copy those too
cal_eye_file = "../calibrate/data/Gus/eye_cal2_" + today_str
cal_time_file = "../calibrate/data/Gus/eye_time2_" + today_str
try:
    copy_this = 'cp ' + cal_eye_file + backup_dir + today_str + '/'
    print('cal_eye', copy_this)
    os.system(copy_this)
    copy_this = 'cp ' + cal_time_file + backup_dir + today_str + '/'
    print('time_eye', copy_this)
    os.system(copy_this)
except:
    pass
print 'Thanks for playing'