import os
import time
if os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
    while os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False and os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
        time.sleep(1)


    partnum = "001"
    device = "Muse"
    filename = "baseline_stroke_study"
    exp_loc= "Baseline_Stroke_Study"

    while os.path.isfile("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Data/" + partnum + "_" + filename + ".csv") == True:
        if int(partnum) >=10:
            partnum = "0" + str(int(partnum) + 1)
        else:
            partnum = "00" + str(int(partnum) + 1)

    os.system('python /home/pi/research_experiments/Experiments/Packages/muse-lsl-master/lsl-record_muse.py '+partnum+' '+device+' '+filename+' '+exp_loc+'')
else:
    exit()
