import os
import time

if os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
    while os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == False and os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
        time.sleep(5)

    os.system('python /home/pi/research_experiments/Experiments/Baseline_Stroke_Study/Task/Baseline_Stroke_Study.py')
else:
    exit()
