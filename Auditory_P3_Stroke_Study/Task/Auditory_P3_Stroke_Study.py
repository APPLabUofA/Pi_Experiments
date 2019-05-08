import time
import os
import sys
from random import randint
from random import shuffle
from datetime import datetime
import numpy
import pygame
import RPi.GPIO as GPIO
from pylsl import StreamInfo, StreamOutlet, local_clock

###variables for filenames and save locations###
partnum = '001'
device = sys.argv[2]
filename = sys.argv[3]
exp_loc = sys.argv[4]
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

###create variables for our sounds###
standard = '/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/low_tone.wav'
target = '/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/high_tone.wav'

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

###initialise pygame###
GPIO.setmode(GPIO.BCM)
pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()
pygame.mixer.init()

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
trig_type = []
delay_length  = []

###set triggers to 0###
GPIO.output(pi2trig(255,0)

###define the number of trials, and tones per trial###
trials = 10
low_rate = 0.8
high_rate = 0.2
low_tone = numpy.zeros(int(trials*low_rate))
high_tone = numpy.ones(int(trials*high_rate))
low_tone_list = low_tone.tolist()
high_tone_list = high_tone.tolist()
tones = low_tone_list + high_tone_list
shuffle(tones)


###wait for button press to start experiment###

exp_start = time.time()
timestamp = local_clock()
outlet.push_sample([3], timestamp)
GPIO.output(pi2trig(3),1)
time.sleep(1)
GPIO.output(pi2trig(3),0)

for i_tone in range(len(tones)):
    ###wait for a random amount of time between tones###
    delay = ((randint(0,500))*0.001)+1.00
    delay_length.append(delay)
    if tones[i_tone] == 0:#low tone
        pygame.mixer.music.load(standard)
        trig_type.append(1)
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([1], timestamp)
        GPIO.output(pi2trig(1),1)
        trig_time.append(time.time() - vid_start) 
    elif tones[i_tone] == 1:#high tone
        pygame.mixer.music.load(target)
        trig_type.append(2)
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([2], timestamp)
        GPIO.output(pi2trig(2),1)
        trig_time.append(time.time() - vid_start) 
    ###playback tone###
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    ###wait for a random amount of time and set the trigger back to zero###
    GPIO.output(pi2trig(255),0)
    time.sleep(delay)

###show the end screen###
timestamp = local_clock()
outlet.push_sample([5], timestamp)
GPIO.output(pi2trig(5),1)
time.sleep(1.0)
GPIO.output(pi2trig(5),0)

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

numpy.savetxt(filename_part, (trig_type,trig_time,delay_length), delimiter=',',fmt="%s")

pygame.display.quit()
pygame.quit()
GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
