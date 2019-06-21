import os
import time

while os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
    time.sleep(5)

while os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False:
    time.sleep(5)

partnum = "001"
device = "Muse"
filename_path = "lsl_auditory_p3_stroke_study_eeg"
exp_loc= "Auditory_P3_Stroke_Study"

while os.path.isfile(f"/home/pi/research_experiments/Experiments/{exp_loc}/Data/{device}/LSL_Data/{partnum}_{filename_path}.csv") == True:
    if int(partnum) >=10:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

os.system(f"muselsl record --type EEG --partnum {partnum} --device {device} --filename_path {filename_path} --exp_loc {exp_loc}")
