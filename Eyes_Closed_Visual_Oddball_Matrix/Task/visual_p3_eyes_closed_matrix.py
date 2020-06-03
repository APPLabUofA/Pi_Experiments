import time
import os
from random import randint
from random import shuffle
import board
import neopixel
import RPi.GPIO as GPIO
from datetime import datetime
import numpy as np
import pandas as pd
import pygame

###setup GPIO pins and initialise pygame###
GPIO.setmode(GPIO.BCM)
##############THIS BREAKS THE LEDs FOR SOME REASON
#pygame.init()
##############DO NOT ENEABLE
pygame.display.init()

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19,18],GPIO.OUT)

###setup pin for push button###
pin = 21
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

##specify which pin we will be controlling the LEDs with##
pin_out = board.D18
led_num = 64

##several colours for the pixels##
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
blank = (0, 0, 0)
brightness = 0.2

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

###variables for filenames and save locations###
partnum = '001'
device = 'Amp'
filename = 'Eyes_Closed_Visual_Oddball_Matrix'
exp_loc = 'Eyes_Closed_Visual_Oddball_Matrix'
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

##setup our neopixels##
pixels = neopixel.NeoPixel(pin_out, led_num, brightness = brightness, auto_write = True)

###define the number of trials, and tones per trial###
trials = 10
low_rate = 0.8
high_rate = 0.2
low_tone = np.zeros(int(trials*low_rate))
high_tone = np.ones(int(trials*high_rate))
low_tone_list = low_tone.tolist()
high_tone_list = high_tone.tolist()
tones = low_tone_list + high_tone_list
shuffle(tones)

###setup variables to record times###
trig_time   = []
trig_type = []
delay_length  = []
resp_time = []

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###make sure pixels are off###
pixels.fill(blank)

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)

###draw fixation###
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()
time.sleep(1)

###wait for button press to start experiment###
time.sleep(1)
##GPIO.wait_for_edge(21,GPIO.RISING)
time.sleep(1)
start_exp = time.time()
pixels.fill(blank)
time.sleep(1)

for i_tone in range(len(tones)):
        delay = ((randint(0,500))*0.001)+1.00
        delay_length.append(delay)
        if tones[i_tone] == 0:#standard
                ###set LEDs as green###
                pixels.fill(green)
                trig = 1
        elif tones[i_tone] == 1:#targets
                ###set LEDs as blue###
                pixels.fill(blue)
                trig = 2
        trig_type.append(trig)
        GPIO.output(pi2trig(trig),1)
        trig_time.append(time.time() - start_exp)
        ###now try and get a response###
        start_resp = time.time()
        wait_resp = 0
        edge_detect = GPIO.wait_for_edge(pin,GPIO.RISING, timeout = 1000)
        if edge_detect is not None:
                GPIO.output(pi2trig(255),0)
                resp = time.time() - start_resp
                resp_time.append(resp)
                GPIO.output(pi2trig(int(tones[i_tone])+3),1)
                time.sleep(1 - resp)
                wait_resp = 1
        GPIO.output(pi2trig(255),0)
        pixels.fill(blank)
        start_resp = time.time()
        edge_detect = GPIO.wait_for_edge(pin,GPIO.RISING, timeout = int(delay*1000))
        if edge_detect is not None and wait_resp == 0:
                GPIO.output(pi2trig(255),0)
                resp = time.time() - start_resp
                resp_time.append(resp)
                GPIO.output(pi2trig(int(tones[i_tone])+3),1)
                time.sleep(delay - resp)
                wait_resp = 1
        else:
                resp_time.append(0)
        GPIO.output(pi2trig(255),0)

##GoPro_LED_Flash(10)
###show the end screen###
GPIO.output(pi2trig(6),1)
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

GPIO.output(pi2trig(255),0)
pygame.display.quit()
pygame.quit()
GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")