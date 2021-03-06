import time
import os

###create a dummy display for pygame###
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import sys
from random import randint
from random import shuffle
from datetime import datetime
import numpy as np
import pandas as pd
import pygame
import RPi.GPIO as GPIO
from pylsl import StreamInfo, StreamOutlet, local_clock

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

###initialise pygame###
GPIO.setmode(GPIO.BCM)
pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()
pygame.display.set_mode((1,1))
pygame.mixer.init()

###variables for filenames and save locations###
partnum = '001'
device = 'Muse'
filename = 'Baseline_Stroke_Study_Updated'
exp_loc = 'Baseline_Stroke_Study'
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

###time for each baseline segment###
baseline_length = 1 ###3 minutes in seconds

###create variables for our sounds###
tone= '/home/pi/Pi_Experiments/Stimuli/Sounds/Auditory_Oddball/1000hz_tone.wav'
ready_tone= '/home/pi/Pi_Experiments/Stimuli/Sounds/Auditory_Oddball/2000hz_tone.wav'

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19,24],GPIO.OUT)

###Setup our function to send triggers###
###trig_type is either 's' or 'r'###
###trig_num must be between 1-15###
def pi2trig(trig_num):
    
    pi_pins = [4,17,27,22,5,6,13,19]
    
    bin_num = list(reversed(bin(trig_num)[2:]))
    
    while len(bin_num) < len(pi_pins):
        bin_num.insert(len(bin_num)+1,str(0))
    
    trig_pins = []
    
    trig_pos = 0
    
    for i_trig in range(len(pi_pins)):
        if bin_num[i_trig] == '1':
            trig_pins.insert(trig_pos,pi_pins[i_trig])
            trig_pos = trig_pos + 1
    
    return trig_pins

###setup variables to record times###
exp_start = []
trig_time   = []

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###play tones to indicate the experiment is ready###
pygame.mixer.music.load(ready_tone)
for i_tone in range(2):
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

###wait for button press to start experiment###
key_pressed = 0
pygame.event.clear()
while key_pressed == 0:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            key_pressed = 1

###send triggers###
exp_start = time.time()
timestamp = local_clock()
outlet.push_sample([1], timestamp)
GPIO.output(pi2trig(1),1)
time.sleep(1)
GPIO.output(pi2trig(1),0)

###play tones at the beginning to indicate start of first three minute segment###
pygame.mixer.music.load(tone)
for i_tone in range(3):
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    time.sleep(0.1)

###send triggers###
trig_time.append(time.time() - exp_start)
timestamp = local_clock()
outlet.push_sample([2], timestamp)
GPIO.output(pi2trig(2),1)
time.sleep(1)
GPIO.output(pi2trig(2),0)

###now wait the first three minutes
time.sleep(baseline_length)

###send triggers###
trig_time.append(time.time() - exp_start)
timestamp = local_clock()
outlet.push_sample([3], timestamp)
GPIO.output(pi2trig(3),1)
time.sleep(1)
GPIO.output(pi2trig(3),0)

###now play the tones again to indicate the end of the first segment and the beginning of the next###
pygame.mixer.music.load(tone)
for i_tone in range(3):
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    time.sleep(0.1)

###send triggers###
trig_time.append(time.time() - exp_start)
timestamp = local_clock()
outlet.push_sample([4], timestamp)
GPIO.output(pi2trig(4),1)
time.sleep(1)
GPIO.output(pi2trig(4),0)

###now wait the second three minutes
time.sleep(baseline_length)

###send triggers###
trig_time.append(time.time() - exp_start)
timestamp = local_clock()
outlet.push_sample([5], timestamp)
GPIO.output(pi2trig(5),1)
time.sleep(1)
GPIO.output(pi2trig(5),0)

###play the tones to indicate the end of the experiment###
pygame.mixer.music.load(tone)
for i_tone in range(3):
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    time.sleep(0.1)

###send triggers###
timestamp = local_clock()
outlet.push_sample([6], timestamp)
GPIO.output(pi2trig(6),1)
time.sleep(1)
GPIO.output(pi2trig(6),0)

###save times###
directory = os.path.dirname("/home/pi/Pi_Experiments/" + exp_loc + "/Data/" + device + "/Trial_Information/")
if not os.path.exists(directory):
    os.makedirs(directory)
        
while os.path.isfile("/home/pi/Pi_Experiments/" + exp_loc + "/Data/" + device + "/Trial_Information/" + partnum + "_" + filename + ".csv") == True:
    if int(partnum) >=10:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

filename_part = ("/home/pi/Pi_Experiments/" + exp_loc + "/Data/" + device + "/Trial_Information/" + partnum + "_" + filename + ".csv")

the_list = [trig_time]
df_list = pd.DataFrame({i:pd.Series(value) for i, value in enumerate(the_list)})
df_list.columns = ['Baseline_Onset_Offset_Time']
df_list.to_csv(filename_part)

pygame.display.quit()
pygame.quit()
GPIO.cleanup()

if os.path.isfile("/home/pi/Pi_Experiments/Stop_EEG2.csv") == True:
    os.remove("/home/pi/Pi_Experiments/Stop_EEG2.csv")
    time.sleep(2)
    os.remove("/home/pi/Pi_Experiments/Stop_EEG1.csv")
    time.sleep(2)
