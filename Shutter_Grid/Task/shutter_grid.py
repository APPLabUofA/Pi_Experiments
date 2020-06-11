import os

os.system('sudo pigpiod')

import time
from random import randint
from random import shuffle
import pigpio
import RPi.GPIO as GPIO
from datetime import datetime
import numpy as np
import pandas as pd
import pygame

###variables for filenames and save locations###
partnum = '001'
device = 'Amp'
filename = 'Shutter_Image'
exp_loc = 'Shutter_Image'
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

###setup GPIO pins and initialise pygame###
pi = pigpio.pi()
GPIO.setmode(GPIO.BCM)
pygame.init()
pygame.display.init()

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

###setup pins for each LCD###
lcd_freq = 17
dc = 50 * 10000

###setup pin for push button###
pin = 26
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

###setup variables to record times###
trial_dc = []
trial_face = []
resp_time = []
resp_type = []
face_num = []

###audio file location###
tone = '/home/pi/Pi_Experiments/Stimuli/Sounds/Auditory_Oddball/low_tone.wav'

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()

x_width = disp_info.current_w
y_height = disp_info.current_h
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
screen = pygame.display.set_mode((x_width, y_height),pygame.FULLSCREEN)

####FOR TESTING ONLY####
##x_width = 400
##y_height = 300
##x_center = x_width/2
##y_center = y_height/2
##screen = pygame.display.set_mode((x_width, y_height),pygame.RESIZABLE)
########################

black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)
grey = pygame.Color(127,127,127)
rect_x = 5
rect_y = 5
screen.fill(white)

###settings to change###
font_colour = black

fixation_colour_outer= black
fixation_length_outer = 4
fixation_size_outer = 3

fixation_colour_inner = white
fixation_length_inner = 3
fixation_size_inner = 1

###create our grid###
grid_size = 9 ###total squares will be this number squared, max is 9 due to current trigger system (i_square * 3 = onset; i_square * 3 + 1 = offset)
fig_style = 3 ###1 = horizontal; 2 = vertical; 3 = repeat gradient
colour_order = [255,0] ###1 = black to white; 2 = white to black
fixation_time = 0 ###number of seconds to focus on each square
pre_time = 0.5
post_time = 0.5
#########################

###determine x and y coordinates for each square###
x_locs = list(np.linspace(0,x_width,(grid_size)+1))
y_locs = list(np.linspace(0,y_height,(grid_size)+1))

###setup our colours (black, greys, white)
grid_colour = []
colour_list = np.linspace(colour_order[0],colour_order[1],(grid_size))
for i_square in range((grid_size)):
    temp = np.zeros(3) + colour_list[i_square]
    grid_colour.append(temp.tolist())

###draw grid###
for i_y in range(len(y_locs)-1):
    if fig_style == 1: ###horizontal bars
        for i_x in range(len(x_locs)-1):
            pygame.draw.rect(screen, grid_colour[i_y], (x_locs[i_x], y_locs[i_y], x_locs[i_x+1], y_locs[i_y+1]),0)
    elif fig_style == 2: ###vertical bars
        for i_x in range(len(x_locs)-1):
            pygame.draw.rect(screen, grid_colour[i_x], (x_locs[i_x], y_locs[i_y], x_locs[i_x+1], y_locs[i_y+1]),0)
    elif fig_style == 3: ###repeat gradient
        for i_x in range(len(x_locs)-1):
            pygame.draw.rect(screen, grid_colour[i_x], (x_locs[i_x], y_locs[i_y], x_locs[i_x+1], y_locs[i_y+1]),0)
        grid_colour.append(grid_colour.pop(0))

###Setup our function to send triggers###
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

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###wait for response###
pygame.display.flip()
time.sleep(0.1)
key_pressed = 0
pygame.event.clear()
while key_pressed == 0:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                key_pressed = 1
time.sleep(0.5)
pi.hardware_PWM(18, lcd_freq, dc)

###draw a fixation over the square to focus on###
if fig_style == 1:###horizontal lines
    ###collapse across x locations###
    x_locs = [0,x_locs[-1]]
elif fig_style == 2: ###vertical lines
    ###collapse across y locations###
    y_locs = [0,y_locs[-1]]

i_square = 0
for i_y in range(len(y_locs)-1):
    for i_x in range(len(x_locs)-1):
        ###update current square###
        i_square += 1
        ###determine center of current square###
        x_center = int(x_locs[i_x] + ((x_locs[i_x+1] - x_locs[i_x])/2))
        y_center = int(y_locs[i_y] + ((y_locs[i_y+1] - y_locs[i_y])/2))
        
        ###get colour of current square###
        crnt_colour = screen.get_at((x_center, y_center))[:3]

        ###draw fixation###
        pygame.draw.line(screen, fixation_colour_outer, (x_center-fixation_length_outer, y_center), (x_center+fixation_length_outer, y_center),fixation_size_outer)
        pygame.draw.line(screen, fixation_colour_outer, (x_center, y_center-fixation_length_outer), (x_center, y_center+fixation_length_outer),fixation_size_outer)
        pygame.draw.line(screen, fixation_colour_inner, (x_center-fixation_length_inner, y_center), (x_center+fixation_length_inner, y_center),fixation_size_inner)
        pygame.draw.line(screen, fixation_colour_inner, (x_center, y_center-fixation_length_inner), (x_center, y_center+fixation_length_inner),fixation_size_inner)
        GPIO.output(pi2trig(((i_square)*3)),1)
        pygame.display.flip()

        ###wait for a bit###
        time.sleep(pre_time)
        GPIO.output(pi2trig(255),0)
        time.sleep(fixation_time)
        GPIO.output(pi2trig(((i_square)*3)+1),1)
        time.sleep(post_time)
        GPIO.output(pi2trig(255),0)

        ###remove fixation###
        pygame.draw.line(screen, crnt_colour, (x_center-fixation_length_outer, y_center), (x_center+fixation_length_outer, y_center),fixation_size_outer)
        pygame.draw.line(screen, crnt_colour, (x_center, y_center-fixation_length_outer), (x_center, y_center+fixation_length_outer),fixation_size_outer)

pi.hardware_PWM(18, lcd_freq, 0)
os.system('sudo killall pigpiod')
pygame.display.quit()
pygame.quit()
GPIO.cleanup()
