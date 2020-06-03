import board
import neopixel
import pygame
from pygame.locals import *
import cv2
import numpy as np
import sys
import time
import RPi.GPIO as GPIO
from datetime import datetime
import numpy as np
import pandas as pd
from random import randint
from random import shuffle
import os

###variables for filenames and save locations###
partnum = '001'
device = 'Amp'
filename = 'Visual_P3_LED_Neopixel_Indoor'
exp_loc = 'Visual_P3_LED_Neopixel_Indoor'
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

###filename of video###
file_name = "/home/pi/research_experiments/Experiments/Visual_P3_LED_Neopixel_Indoor/Task/Bike_Video.mp4"

###setup GPIO pins and initialise pygame###
GPIO.setmode(GPIO.BCM)

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19,18],GPIO.OUT)

###setup pin for push button###
pin = 21
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

##specify which pin we will be controlling the LEDs with##
pin_out = board.D18
led_num = 6

##several colours for the pixels##
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
blank = (0, 0, 0)
brightness = 0.2

###setup variables to record times###
trig_time   = []
trig_type = []
delay_length  = []
resp_time = []

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

###play video, rather than use webcam###
camera = cv2.VideoCapture(file_name)

###initialise pygame###
##pygame.init()
pygame.display.init()

##setup our neopixels##
pixels = neopixel.NeoPixel(pin_out, led_num, brightness = brightness, auto_write = True)

###setup some screen variables###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
pygame.display.set_caption("OpenCV camera stream on Pygame")
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###make sure pixels are off###
pixels.fill(blank)

###show first frame and then wait for a button press###
ret, frame = camera.read()
screen.fill([0,0,0])
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
frame = np.fliplr(frame)
frame = np.rot90(frame)
frame = pygame.surfarray.make_surface(frame)
frame_dims = pygame.Surface.get_size(frame)
screen.blit(frame, (x_center - (frame_dims[0]/2),y_center - (frame_dims[1]/2)))
pygame.display.update()
time.sleep(1)
GPIO.wait_for_edge(21,GPIO.RISING)
time.sleep(1)
start_exp = time.time()
for i_blink in range(25):
    GPIO.output(pi2trig(10),1)
    pixels.fill(red)
    time.sleep(0.1)
    GPIO.output(pi2trig(255),0)
    pixels.fill(blank)
    time.sleep(randint(100,500)*0.001)
time.sleep(1)
GPIO.output(pi2trig(5),0)
pixels.fill(blank)
time.sleep(1)

###run the main experiment###

try:
    start_exp = time.time()
    while (time.time() - start_exp <= 10):

        ret, frame = camera.read()

        screen.fill([0,0,0])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.fliplr(frame)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        frame_dims = pygame.Surface.get_size(frame)
        screen.blit(frame, (x_center - (frame_dims[0]/2),y_center - (frame_dims[1]/2)))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                sys.exit(0)

    for i_blink in range(25):
        GPIO.output(pi2trig(11),1)
        pixels.fill(red)
        time.sleep(0.1)
        GPIO.output(pi2trig(255),0)
        pixels.fill(blank)
        time.sleep(randint(100,500)*0.001)

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
except (KeyboardInterrupt,SystemExit):
    pygame.quit()
    cv2.destroyAllWindows()
