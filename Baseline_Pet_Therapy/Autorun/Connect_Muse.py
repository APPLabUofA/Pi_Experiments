import os
import time

time.sleep(5)

tries = 1
while os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False and tries < 11 and os.path.isfile("/home/pi/research_experiments/Muse_Shutdown.txt") == False:
    os.system('python /home/pi/research_experiments/Experiments/Packages/muse-lsl-master/muse-lsl-connect.py --name Muse-6480')
    if os.path.isfile("/home/pi/research_experiments/Stop_EEG1.csv") == False:
        tries += 1

time.sleep(5)
os.remove("/home/pi/research_experiments/Muse_Shutdown.txt")
os.system("sudo shutdown -h now")
