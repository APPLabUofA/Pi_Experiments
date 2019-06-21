import os
import time

while os.path.isfile("/home/pi/research_experiments/Muse_Continue.txt") == False:
    time.sleep(5)

while os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == False:
    time.sleep(5)

os.system('python /home/pi/research_experiments/Experiments/Auditory_P3_Stroke_Study/Task/Auditory_P3_Stroke_Study.py')

time.sleep(5)
os.system("sudo shutdown -h now")
