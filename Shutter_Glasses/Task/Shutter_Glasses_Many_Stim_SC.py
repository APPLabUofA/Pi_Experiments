import time
import os
import sys
from random import randint
from random import shuffle
from datetime import datetime
import numpy as np
import pandas as pd
import pygame
import RPi.GPIO as GPIO

###variables for filenames and save locations###
partnum = '001'
device = 'Amp'
filename = 'Shutter_Glasses'
exp_loc = 'Shutter_Glasses'
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

###initialise pygame###
GPIO.setmode(GPIO.BCM)
pygame.init()
pygame.display.init()

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)
rect_size = 100
rect_green = (0,255,0)
rect_blue = (0,0,255)
rect_black = (0,0,0)
rect_white = (255,255,255)

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19,18],GPIO.OUT)

###make sure LED is off###
GPIO.output(18,0)

###setup pin for push button###
pin = 26
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

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
trig_time   = []
trig_type = []
delay_length  = []
resp_time = []

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###define the number of trials, and tones per trial###
trials = 5
low_rate = 0.8
high_rate = 0.2
low_tone = np.zeros(int(trials*low_rate))
high_tone = np.ones(int(trials*high_rate))
low_tone_list = low_tone.tolist()
high_tone_list = high_tone.tolist()
tones = low_tone_list + high_tone_list
shuffle(tones)

###draw fixation###
line1 = pygame.draw.line(screen, rect_white, (x_center-10, y_center), (x_center+10, y_center),4)
line2 = pygame.draw.line(screen, rect_white, (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()

###wait for button press to start experiment###
time.sleep(1)
##GPIO.output(pi2trig(255),0)
##GPIO.wait_for_edge(pin,GPIO.RISING)
##time.sleep(1)
##GPIO.wait_for_edge(pin,GPIO.RISING)
##time.sleep(1)
##GPIO.wait_for_edge(pin,GPIO.RISING)

###remove fixation###
line1 = pygame.draw.line(screen, rect_black, (x_center-10, y_center), (x_center+10, y_center),4)
line2 = pygame.draw.line(screen, rect_black, (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()

#####flash LED 10 times, with a random delay between each flash###
##for i_flash in range(24):
##    GPIO.output(18,1)
##    GPIO.output(pi2trig(10),1)
##    time.sleep(0.1)
##    GPIO.output(pi2trig(10),0)
##    GPIO.output(18,0)
##    time.sleep(randint(100,500)*0.001)

###start experiment###
exp_start = time.time()
GPIO.output(pi2trig(8),1)
time.sleep(0.5)
GPIO.output(pi2trig(255),0)
time.sleep(0.5)

###experiment###
for i_tone in range(len(tones)):
    ###wait for a random amount of time between tones###
    delay = ((randint(0,1000))*0.001)+2
    delay_length.append(delay)
    if tones[i_tone] == 0:#square
        stim1 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)-200),(y_center-(rect_size*2)),rect_size,rect_size))
        stim2 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)),(y_center-(rect_size*2)),rect_size,rect_size))
        stim3 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)+200),(y_center-(rect_size*2)),rect_size,rect_size))
        
        stim4 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)-200),(y_center-(rect_size/2)),rect_size,rect_size))
        stim5 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)),(y_center-(rect_size/2)),rect_size,rect_size))
        stim6 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)+200),(y_center-(rect_size/2)),rect_size,rect_size))
        
        stim7 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)-200),(y_center+(rect_size)),rect_size,rect_size))
        stim8 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)),(y_center+(rect_size)),rect_size,rect_size))
        stim9 = pygame.draw.rect(screen, rect_white , ((x_center-(rect_size/2)+200),(y_center+(rect_size)),rect_size,rect_size))
        trig_type.append(1)
    elif tones[i_tone] == 1:#triangle
        stim1 = pygame.draw.circle(screen, rect_white , (int(x_center-200),int(y_center-(rect_size*2)+(rect_size/2))),int(rect_size/2))
        stim2 = pygame.draw.circle(screen, rect_white , (int(x_center),int(y_center-(rect_size*2)+(rect_size/2))),int(rect_size/2))
        stim3 = pygame.draw.circle(screen, rect_white , (int(x_center+200),int(y_center-(rect_size*2)+(rect_size/2))),int(rect_size/2))

        stim4 = pygame.draw.circle(screen, rect_white , (int(x_center-200),int(y_center)),int(rect_size/2))
        stim5 = pygame.draw.circle(screen, rect_white , (int(x_center),int(y_center)),int(rect_size/2))
        stim6 = pygame.draw.circle(screen, rect_white , (int(x_center+200),int(y_center)),int(rect_size/2))

        stim7 = pygame.draw.circle(screen, rect_white , (int(x_center-200),int(y_center+(rect_size*2)-(rect_size/2))),int(rect_size/2))
        stim8 = pygame.draw.circle(screen, rect_white , (int(x_center),int(y_center+(rect_size*2)-(rect_size/2))),int(rect_size/2))
        stim9 = pygame.draw.circle(screen, rect_white , (int(x_center+200),int(y_center+(rect_size*2)-(rect_size/2))),int(rect_size/2))
        trig_type.append(2)
    ###draw stim and send trigger### 
    trig_time.append(time.time() - exp_start)
    GPIO.output(pi2trig(int(tones[i_tone])+1),1)
    pygame.display.update([stim1,stim2,stim3,stim4,stim5,stim6,stim7,stim8,stim9])
    ###wait for a random amount of time and set the trigger back to zero###
    time.sleep(0.005)
    GPIO.output(pi2trig(255),0)
    ###now try and get a response###
    start_resp = time.time()
    edge_detect = GPIO.wait_for_edge(pin,GPIO.RISING, timeout = int(delay * 1000))
    if edge_detect is not None:  
        resp = time.time() - start_resp
        resp_time.append(resp)
        GPIO.output(pi2trig(int(tones[i_tone])+3),1)
        time.sleep(delay - resp)
        GPIO.output(pi2trig(255),0)
    else:
        resp_time.append(0)
        GPIO.output(pi2trig(255),0)
    if tones[i_tone] == 0:#square
        stim1 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)-200),(y_center-(rect_size*2)),rect_size,rect_size))
        stim2 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)),(y_center-(rect_size*2)),rect_size,rect_size))
        stim3 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)+200),(y_center-(rect_size*2)),rect_size,rect_size))
        
        stim4 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)-200),(y_center-(rect_size/2)),rect_size,rect_size))
        stim5 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)),(y_center-(rect_size/2)),rect_size,rect_size))
        stim6 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)+200),(y_center-(rect_size/2)),rect_size,rect_size))
        
        stim7 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)-200),(y_center+(rect_size)),rect_size,rect_size))
        stim8 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)),(y_center+(rect_size)),rect_size,rect_size))
        stim9 = pygame.draw.rect(screen, rect_black , ((x_center-(rect_size/2)+200),(y_center+(rect_size)),rect_size,rect_size))
    elif tones[i_tone] == 1:#triangle
        stim1 = pygame.draw.circle(screen, rect_black , (int(x_center-200),int(y_center-(rect_size*2)+(rect_size/2))),int(rect_size/2))
        stim2 = pygame.draw.circle(screen, rect_black , (int(x_center),int(y_center-(rect_size*2)+(rect_size/2))),int(rect_size/2))
        stim3 = pygame.draw.circle(screen, rect_black , (int(x_center+200),int(y_center-(rect_size*2)+(rect_size/2))),int(rect_size/2))

        stim4 = pygame.draw.circle(screen, rect_black , (int(x_center-200),int(y_center)),int(rect_size/2))
        stim5 = pygame.draw.circle(screen, rect_black , (int(x_center),int(y_center)),int(rect_size/2))
        stim6 = pygame.draw.circle(screen, rect_black , (int(x_center+200),int(y_center)),int(rect_size/2))

        stim7 = pygame.draw.circle(screen, rect_black , (int(x_center-200),int(y_center+(rect_size*2)-(rect_size/2))),int(rect_size/2))
        stim8 = pygame.draw.circle(screen, rect_black , (int(x_center),int(y_center+(rect_size*2)-(rect_size/2))),int(rect_size/2))
        stim9 = pygame.draw.circle(screen, rect_black , (int(x_center+200),int(y_center+(rect_size*2)-(rect_size/2))),int(rect_size/2))
    pygame.display.update([stim1,stim2,stim3,stim4,stim5,stim6,stim7,stim8,stim9])
    GPIO.output(pi2trig(int(tones[i_tone]+5)),1)
    time.sleep(1.0)
    GPIO.output(pi2trig(255),0)
    time.sleep(0.005)
    
##GoPro_LED_Flash(10)
###show the end screen###
GPIO.output(pi2trig(7),1)
time.sleep(0.5)
GPIO.output(pi2trig(255),0)
time.sleep(0.5)

###save times###
while os.path.isfile("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/Trial_Information/" + partnum + "_" + filename + ".csv") == True:
    if int(partnum) >= 9:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/Trial_Information/" + partnum + "_" + filename + ".csv")

the_list = [date, trig_type,trig_time,delay_length,resp_time]
df_list = pd.DataFrame({i:pd.Series(value) for i, value in enumerate(the_list)})
df_list.columns = ['Date','Trigger_Type','Trigger_Onset_Time','Trial_Delay','Response_Time']
df_list.to_csv(filename_part)

#####flash LED 10 times, with a random delay between each flash###
##for i_flash in range(24):
##    GPIO.output(18,1)
##    GPIO.output(pi2trig(11),1)
##    time.sleep(0.1)
##    GPIO.output(pi2trig(255),0)
##    GPIO.output(18,0)
##    time.sleep(randint(100,500)*0.001)

GPIO.output(pi2trig(255),0)
pygame.display.quit()
pygame.quit()
GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
