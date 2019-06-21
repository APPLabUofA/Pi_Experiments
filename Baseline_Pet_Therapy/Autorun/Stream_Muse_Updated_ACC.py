import os
import time

while os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False:
    time.sleep(1)

partnum = "001"
device = "Muse"
filename_path = "baseline_pet_therapy_acc"
exp_loc = "Baseline_Pet_Therapy"

while os.path.isfile(f"/home/pi/research_experiments/Experiments/{exp_loc}/Data/{device}/LSL_Data/{partnum}_{filename_path}.csv") == True:
    if int(partnum) >=10:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

os.system(f"muselsl record --type ACC --partnum {partnum} --device {device} --filename_path {filename_path} --exp_loc {exp_loc}")

