import os
import time

while os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == False:
    time.sleep(5)

os.system('python /home/pi/research_experiments/Experiments/Baseline_Pet_Therapy/Task/Baseline_Pet_Therapy_Updated.py')
