import os
import time

if os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
    tries = 1
    while os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False and tries < 11 and os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
        os.system('python /home/pi/research_experiments/Experiments/Packages/muse-lsl-master/muse-lsl-connect.py --name Muse-1E65')
        if os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False and os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
            tries += 1

    if tries == 11:
        os.system("sudo shutdown -h now")
else:
    exit()
