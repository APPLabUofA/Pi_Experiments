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
GPIO.output([23,24],0)
left_eye = GPIO.PWM(23,lcd_freq)
right_eye = GPIO.PWM(24,lcd_freq)
left_eye.start(0)
right_eye.start(0)
dc = [0.1,6.0,50.0]
hz = [17,17,17]

###baseline variables###
baseline_length = 5

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
rect_x = 656
rect_y = 606
screen.fill(white)

font_colour = black
fixation_colour = black
fixation_length = 5
fixation_size = 1

###define stimulus locations###
tone_resp = os.path.join('/home/pi/Experiments/Stimuli/Sounds/Auditory_Oddball', '1000hz_tone.wav')

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
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###setup our instruction screens###
myfont = pygame.font.SysFont('Times New Roman', 20)
open_block = myfont.render('Focus on the fixation for 3 minutes. Press the space bar to begin.', True, font_colour)
end_instr = myfont.render('Congratulations! You have finished the experiment! Contact the experimenter and press the space bar to close the task.', True, font_colour)
instr = [open_block,open_block]

open_block_size = (x_center-((open_block.get_rect().width)/2),y_center+((open_block.get_rect().height))+200)
end_instr_size = (x_center-((end_instr.get_rect().width)/2),y_center+((end_instr.get_rect().height))+200)
instr_size = [open_block_size,open_block_size]

###draw fixation and determine block order###
block_order = range(len(hz))
shuffle(block_order)
pygame.draw.line(screen, fixation_colour, (x_center-fixation_length, y_center), (x_center+fixation_length, y_center),fixation_size)
pygame.draw.line(screen, fixation_colour, (x_center, y_center-fixation_length), (x_center, y_center+fixation_length),fixation_size)

for i_block in range(len(block_order)):
    ###show instructions###
    screen.blit(instr[0],instr_size[0])
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

    ###remove instructions###
    pygame.draw.rect(screen, white, (0, y_center+200, x_width, y_height),0)
    pygame.display.flip()
    ###change duty cycle and hz###
    left_eye.ChangeDutyCycle(dc[block_order[i_block]])
    right_eye.ChangeDutyCycle(dc[block_order[i_block]])
    left_eye.ChangeFrequency(hz[block_order[i_block]])
    right_eye.ChangeFrequency(hz[block_order[i_block]])
    time.sleep(5)
    ###start task###
    GPIO.output(pi2trig(((block_order[i_block]+1)*10)+1),1)
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    time.sleep(baseline_length)
    GPIO.output(pi2trig(((block_order[i_block]+1)*10)+2),1)
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    time.sleep(1)
    ###play tone###
    pygame.mixer.music.load(tone_resp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    ###stop glasses###
    left_eye.ChangeDutyCycle(0)
    right_eye.ChangeDutyCycle(0)
    time.sleep(1)

#####experiment is finished###
#####display instructions and reset triggers###
left_eye.stop()
right_eye.stop()
screen.fill(pygame.Color("white"))
screen.blit(end_instr,end_instr_size)
pygame.display.flip()
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
time.sleep(1)
pygame.display.quit()
pygame.quit()
GPIO.cleanup()
