import time
import os
from random import randint
from random import shuffle
import RPi.GPIO as GPIO
from datetime import datetime
import numpy as np
import pandas as pd
import pygame

###setup GPIO pins and initialise pygame###
GPIO.setmode(GPIO.BCM)
pygame.init()
pygame.display.init()

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19,23,24],GPIO.OUT)

###setup pins for each LCD###
lcd_freq = 15
shutter_time = 5
GPIO.output([23,24],0)
left_eye = GPIO.PWM(23,lcd_freq)
right_eye = GPIO.PWM(24,lcd_freq)
left_eye.start(0)
right_eye.start(0)

###setup pin for push button###
pin = 26
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

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

def play_sound(sound_file,trig_num):
    pygame.mixer.music.load(sound_file)
    GPIO.output(pi2trig(trig_num),1)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    GPIO.output(pi2trig(255),0)

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_width = disp_info.current_w
y_height = disp_info.current_h
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)

###define tones used for opening and closing eyes###
tone_resp= os.path.join('/home/pi/Experiments/Stimuli/Sounds/Auditory_Oddball', '1000hz_tone.wav')
eyes_closed = os.path.join('/home/pi/Experiments/Stimuli/Sounds', 'eyes_closed.wav')
eyes_open = os.path.join('/home/pi/Experiments/Stimuli/Sounds', 'eyes_open.wav')

###now we will run through the main task###
###each trial will go something like this###
###close eyes > start flash > tone to open eyes > watch flash for 10 seconds > beep to close eyes > response > stop flash###
max_thresh_trials = 50

dc_incr = 0.2
crnt_dc = 5

correct_trials = []
incorrect_trials = []
correct_dc = []
incorrect_dc = []
correct_tracker = 0
incorrect_tracker = 0
thresh_thresh = 10

###may be an idea to look at the previous 10 trials and stop once we get 3 correct and incorrect?###
thresh = 1

while thresh == 1:

    ###check to see if they got 2 consecutive correct trials###
    if correct_tracker == 1:
        correct_tracker = 0
        crnt_dc = crnt_dc - dc_incr
    ###check if they got the previous trial incorrect###
    elif len(incorrect_trials) > 0 and incorrect_trials[len(incorrect_trials)-1] == 1:
        crnt_dc = crnt_dc + dc_incr

    ###remove fixation###
    pygame.draw.rect(screen, black, (x_center-200, y_center-200, x_center+200, y_center+200),0)
    pygame.display.flip()

    ###now show the maximum dc###
    left_eye.ChangeDutyCycle(crnt_dc)
    right_eye.ChangeDutyCycle(crnt_dc)

    ###redraw fixation###
    pygame.draw.line(screen, (255, 255, 255), (x_center-200, y_center), (x_center+200, y_center),80)
    pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-200), (x_center, y_center+200),80)
    pygame.display.flip()
    
    ###play a tone to tell the participant to open their eyes###
    play_sound(eyes_open,0)
    time.sleep(1)

    ###wait some time###
    time.sleep(3)

    ###play a tone to tell the participant to close their eyes###
    play_sound(eyes_closed,0)
    time.sleep(1)

    ###now show the minimum dc###
    left_eye.ChangeDutyCycle(0)
    right_eye.ChangeDutyCycle(0)

    ###play tone telling participant to respond###
    play_sound(tone_resp,0)

    ###wait for a response from the participant###
    start_time = time.time()
    key_pressed = 0
    pygame.event.clear()
    while key_pressed == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    key_pressed = 'UP'
                    correct_trials.append(1)
                    incorrect_trials.append(0)
                    correct_dc.append(crnt_dc)
                    incorrect_dc.append(0)
                    correct_tracker += 1
                elif event.key == pygame.K_DOWN:
                    key_pressed = 'DOWN'
                    correct_trials.append(0)
                    incorrect_trials.append(1)
                    correct_dc.append(0)
                    incorrect_dc.append(crnt_dc)
                    correct_tracker = 0
                    incorrect_tracker += 1
            pygame.event.pump()

    time.sleep(0.5)
    
    ###check if 50% of previous 6 trials are incorrect###
    if len(correct_trials) >= thresh_thresh:
        total_correct = [x for x in correct_trials[-thresh_thresh:] if x == 1]
        total_correct = np.sum(total_correct)
        total_incorrect = [x for x in incorrect_trials[-thresh_thresh:] if x == 1]
        total_incorrect = np.sum(total_incorrect)
        ###stop once we have a certain number of incorrect trials within a certain number of trials###
        if total_incorrect == thresh_thresh/2:
            thresh = 0
    ###end thresholding if too many trials have passed###
    if len(correct_trials) == max_thresh_trials:
        thresh = 0
        total_correct = [x for x in correct_trials[-(thresh_thresh*2):] if x == 1]
        total_correct = np.sum(total_correct)
        total_incorrect = [x for x in incorrect_trials[-(thresh_thresh*2):] if x == 1]
        total_incorrect = np.sum(total_incorrect)

###find mean dc for last 3 correct and incorrect trials###
mean_dc_correct = [x for x in correct_dc[-thresh_thresh:] if x > 0]
mean_dc_incorrect = [x for x in incorrect_dc[-thresh_thresh:] if x > 0]

mean_dc_correct = np.mean(mean_dc_correct)
mean_dc_incorrect = np.mean(mean_dc_incorrect)

###get correct and incorrect responses###
print("THESE ARE CORRECT TRIALS")
print(mean_dc_correct)
print("THESE ARE INCORRECT TRIALS")
print(mean_dc_incorrect)

GPIO.output(pi2trig(255),0)
pygame.display.quit()
pygame.quit()
GPIO.cleanup()
