import os
import time

while os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
    time.sleep(5)

tries = 1
while os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False and tries < 11 and os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == True:
    os.system('python /home/pi/research_experiments/Experiments/Packages/muse-lsl-master/muse-lsl-connect.py --name Muse-1E65')
    if os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False and os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == True:
        tries += 1

if tries == 11:
    os.system("sudo shutdown -h now")
