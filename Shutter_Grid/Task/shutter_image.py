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
lcd_freq = 17.0
dc = 50.0

###setup pin for push button###
pin = 26
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

###setup variables to record times###
trial_dc = []
trial_face = []
resp_time = []
resp_type = []
face_num = []

###setup the display screen and fixation###
##pygame.mouse.set_visible(0)
##disp_info = pygame.display.Info()
##x_width = disp_info.current_w
##y_height = disp_info.current_h
##x_center = disp_info.current_w/2
##y_center = disp_info.current_h/2
##screen = pygame.display.set_mode((x_width, y_height),pygame.FULLSCREEN)

####FOR TESTING ONLY####
x_width = 400
y_height = 300
x_center = x_width/2
y_center = y_height/2
screen = pygame.display.set_mode((x_width, y_height),pygame.RESIZABLE)
########################

black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)
grey = pygame.Color(127,127,127)
rect_x = 5
rect_y = 5
screen.fill(white)
font_colour = black

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

###setup our word###
myfont = pygame.font.SysFont('Arial', 800, bold = True)
instr = myfont.render('C-19', True, font_colour)
instr_size = (x_center-((instr.get_rect().width)/2),y_center-((instr.get_rect().height)/2))

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

###move fixation across screen###

timing_stuff = []
while [y_pos,x_pos]  != stop_scan:
    if x_dir == 1: ###move right###
        while x_width - x_pos != rect_x:
            start = time.time()
            ###draw fixation at current pixel###
            screen.fill(white)
            screen.blit(instr,instr_size)
            pygame.draw.rect(screen, grey, (x_pos, y_pos, rect_x, rect_y),0)
            pygame.display.flip()

            ###update current pixel###
            x_pos += 1

            ###wait a bit###
##            time.sleep(pixel_time)
            timing_stuff.append(time.time() - start)

        prev_row = y_pos
        x_dir = 2
        print(np.mean(timing_stuff))
        print(np.median(timing_stuff))
        sss

    elif x_dir == 2: ###move left###
        while x_pos > x_min:
            start = time.time()
            ###draw fixation at current pixel###
            screen.fill(white)
            screen.blit(instr,instr_size)
            pygame.draw.rect(screen, grey, (x_pos, y_pos, rect_x, rect_y),0)
            pygame.display.flip()

            ###update current pixel###
            x_pos -= 1

            ###wait a bit###
##            time.sleep(pixel_time)
            timing_stuff.append(time.time() - start)

        prev_row = y_pos
        x_dir = 1
        print(np.mean(timing_stuff))
        print(np.median(timing_stuff))
        dsfds
        
    ###move down unless we are done scanning###
    if [y_pos,x_pos]  != stop_scan:
        for i_y in range(rect_y):
            start = time.time()
            y_pos += 1
            ###draw fixation at current pixel###
            screen.fill(white)
            screen.blit(instr,instr_size)
            pygame.draw.rect(screen, grey, (x_pos, y_pos, rect_x, rect_y),0)
            pygame.display.flip()
##            time.sleep(pixel_time)
            timing_stuff.append(time.time() - start)
        print(np.mean(timing_stuff))
        print(np.median(timing_stuff))

GPIO.output(pi2trig(255),0)
os.system(' sudo killall pigpiod')
pygame.display.quit()
pygame.quit()
GPIO.cleanup()
