import os
import time

time.sleep(5)

while os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == False and os.path.isfile("/home/pi/research_experiments/Muse_Shutdown.txt") == False:
    time.sleep(5)

os.system('python /home/pi/research_experiments/Experiments/Baseline_Pet_Therapy/Task/Baseline_Pet_Therapy.py')
