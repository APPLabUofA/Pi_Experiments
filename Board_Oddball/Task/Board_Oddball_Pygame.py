import os
from random import randint, shuffle
import numpy as np
import pygame
import RPi.GPIO as GPIO

device = 'amp'
trials = 25

###get GPIO pins ready###
GPIO.setmode(GPIO.BCM)
pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()
pygame.mixer.init()

###initialise pygame###
###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
##screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.RESIZABLE)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

###setup pin for push button###
GPIO.setup(26,GPIO.IN,pull_up_down=GPIO.PUD_UP)

###Setup our function to send triggers###
###trig_type is either 's' or 'r'###
###trig_num must be between 1-15###
def pi2trig(trig_num):
    pi_pins = [4,17,27,22,5,6,13,19]
    
    bin_num = list(reversed(bin(trig_num)[2:]))
    
    while len(bin_num) < 8:
        bin_num.insert(len(bin_num)+1,str(0))
    
    trig_pins = []
    
    trig_pos = 0
    
    for i_trig in range(8):
        if bin_num[i_trig] == '1':
            trig_pins.insert(trig_pos,pi_pins[i_trig])
            trig_pos = trig_pos + 1
    
    return trig_pins

def continue_exp(flip):
    key_pressed = 0
    pygame.event.clear()
    if flip == 0:
        while key_pressed == 0:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    key_pressed = 1
    else:
        pygame.display.flip()
        pygame.time.wait(1000)
        while key_pressed == 0:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    key_pressed = 1
                    
def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue


##### Define variables #####
partnum = "001"
exp_start = []
trial_type = []
trial_delay = []
trial_time = []

###setup our sound stimuli###
low_rate = 0.8
high_rate = 0.2
low_tone = np.zeros(int(trials*low_rate))
high_tone = np.ones(int(trials*high_rate))
low_tone_list = low_tone.tolist()
high_tone_list = high_tone.tolist()
tones = low_tone_list + high_tone_list
shuffle(tones)

target_file = '/home/pi/Experiments/Sounds/2000hz_tone.wav'
standard_file = '/home/pi/Experiments/Sounds/1000hz_tone.wav'

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###wait for button press to start experiment###
pygame.mixer.music.load('/home/pi/Experiments/Sounds/ready.wav')
pygame.mixer.music.play()
wait_for_sound()
time.sleep(1)
GPIO.wait_for_edge(26,GPIO.RISING)
time.sleep(1)
GPIO.wait_for_edge(26,GPIO.RISING)
time.sleep(1)
GPIO.wait_for_edge(26,GPIO.RISING)
exp_run = 1

GPIO.output(pi2trig(ticks),1)
pygame.mixer.music.load('/home/pi/Experiments/Sounds/countdown_10.wav')
pygame.mixer.music.play()
wait_for_sound()
GPIO.output(pi2trig(ticks),0)
ticks += 1
time.sleep(0.01)
GPIO.output(pi2trig(ticks),1)
time.sleep(0.01)
GPIO.output(pi2trig(ticks),0)
ticks += 1

start_exp = pygame.time.get_ticks()

for i_trial in range(len(tones)):
    delay = ((randint(0,500))+1000)
    trial_delay.append(delay)
    ###present our sound###
    if tones[i_trial] == 0:###standard
        trial_sound_order.append(standard_sound)
        trial_type.append(1)
        GPIO.output(pi2trig(1),1)
        trial_time.append(pygame.time.get_ticks() - start_exp)
        play_sound(standard_file)
    elif tones[i_trial] == 1:###target
        trial_sound_order.append(target_sound)
        trial_type.append(2)
        GPIO.output(pi2trig(2),1)
        trial_time.append(pygame.time.get_ticks() - start_exp)
        play_sound(target_file)
    pygame.time.wait(int(delay/2))
    GPIO.output(pi2trig(255),0)
    pygame.time.wait(int(delay/2))
    
###end experiment###
GPIO.output(pi2trig(255),1)
pygame.mixer.music.load('/home/pi/Experiments/Sounds/shut_down.wav')
pygame.mixer.music.play()

###save times###
while os.path.isfile(("/home/pi/Experiments/Board_Oddball/Data/" + device + "/Trial_Info/%s_board_oddball_" + device + ".csv")%(partnum)) == True:
    partnum = '00'+str(int(partnum)+1)
    if int(partnum) > 9:
        partnum = '0' + str(int(partnum))

filename    = ("%s_board_oddball_" + device)%(partnum)
filename_part = ("/home/pi/Experiments/Board_Oddball/Data/" + device + "/Trial_Info/%s.csv")%filename

np.savetxt(filename_part, (trial_type,trial_delay, trial_time), delimiter=',',fmt="%s")

GPIO.cleanup()
      
pygame.time.wait(1000)
pygame.quit()
