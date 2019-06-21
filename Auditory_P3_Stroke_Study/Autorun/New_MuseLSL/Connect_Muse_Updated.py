import os
import time

while os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
    time.sleep(5)

tries = 1
while os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False and tries < 11 and os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == True:
    os.system('muselsl stream --name Muse-6480 --acc --gyro')
    if os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False and os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == True:
        tries += 1

if tries == 11:
    os.system("sudo shutdown -h now")
