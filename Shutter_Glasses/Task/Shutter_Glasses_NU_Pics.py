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
filename = 'Shutter_Glasses_NU_Pics'
exp_loc = 'Shutter_Glasses'
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

nature_loc = '/home/pi/research_experiments/Experiments/Shutter_Glasses/Images/Nature/'
urban_loc = '/home/pi/research_experiments/Experiments/Shutter_Glasses/Images/Urban/'
face_loc = '/home/pi/research_experiments/Experiments/Shutter_Glasses/Images/Faces/'
scrambled_face_loc = '/home/pi/research_experiments/Experiments/Shutter_Glasses/Images/Scrambled_Faces/'

nature_num_1 = list(range(50))
urban_num_1 = list(range(50))
face_num_1 = list(range(59))
scrambled_face_num_1 = list(range(60))

shuffle(nature_num_1)
shuffle(urban_num_1)
shuffle(face_num_1)
shuffle(scrambled_face_num_1)

nature_num_2 = list(range(50))
urban_num_2 = list(range(50))
face_num_2 = list(range(59))
scrambled_face_num_2 = list(range(60))

shuffle(nature_num_2)
shuffle(urban_num_2)
shuffle(face_num_2)
shuffle(scrambled_face_num_2)

nature_num = nature_num_1 + nature_num_2
urban_num = urban_num_1 + urban_num_2
face_num = face_num_1 + face_num_2
scrambled_face_num = scrambled_face_num_1 + scrambled_face_num_2

nature_num = [x+1 for x in nature_num]
urban_num = [x+1 for x in urban_num]
face_num = [x+1 for x in face_num]
scrambled_face_num = [x+1 for x in scrambled_face_num]

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
rect_size = 600
rect_x = 656
rect_y = 606
border_size = 50
rect_red = (196,0,0)
rect_green = (0,255,0)
rect_blue = (0,0,255)
rect_black = (0,0,0)
rect_white = (255,255,255)
rect_grey = (127.5,127.5,127.5)

###define the number of trials, and tones per trial###
trials = 250
nature_rate = 0.40
urban_rate = 0.40
face_rate = 0.10
scrambled_face_rate = 0.10
nature_trials = (np.zeros(int(trials*nature_rate))+1).tolist()
urban_trials = (np.zeros(int(trials*urban_rate))+2).tolist()
face_trials = (np.zeros(int(trials*face_rate))+3).tolist()
scrambled_face_trials = (np.zeros(int(trials*scrambled_face_rate))+4).tolist()

nature_num = nature_num[0:len(nature_trials)]
urban_num = urban_num[0:len(urban_trials)]
face_num = face_num[0:len(face_trials)]
scrambled_face_num = scrambled_face_num[0:len(scrambled_face_trials)]

nature_trials = list(zip(nature_trials,nature_num))
urban_trials = list(zip(urban_trials,urban_num))
face_trials = list(zip(face_trials,face_num))
scrambled_face_trials = list(zip(scrambled_face_trials,scrambled_face_num))

all_trials = nature_trials + urban_trials + face_trials + scrambled_face_trials
shuffle(all_trials)

stim_time = 3

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
pic_num = []

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###setup our instruction screens###
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 20)
instructions_1 = myfont.render('Press the button each time you see an image of a face. ', True, white)
instructions_2 = myfont.render('When you are ready to start, press the button.', True, white)
done_3 = myfont.render('All done! Press the button to exit.', True, white)

###draw fixation###
##pygame.draw.rect(screen, rect_white , ((x_center-((rect_x+border_size)/2)),(y_center-((rect_y+border_size)/2)),rect_x+border_size,rect_y+border_size))
screen.blit(instructions_1,(x_center-((instructions_1.get_rect().width)/2),y_center + ((instructions_1.get_rect().height)*1)+10))
screen.blit(instructions_2,(x_center-((instructions_2.get_rect().width)/2),y_center + ((instructions_2.get_rect().height)*2)+10))
##line3 = pygame.draw.line(screen, rect_black, (x_center-11, y_center), (x_center+11, y_center),5)
##line4 = pygame.draw.line(screen, rect_black, (x_center, y_center-11), (x_center, y_center+11),5)
line1 = pygame.draw.line(screen, rect_white, (x_center-10, y_center), (x_center+10, y_center),4)
line2 = pygame.draw.line(screen, rect_white, (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()

###wait for button press to start experiment###
time.sleep(1)
GPIO.output(pi2trig(255),0)
GPIO.wait_for_edge(pin,GPIO.RISING)
time.sleep(1)
GPIO.wait_for_edge(pin,GPIO.RISING)
time.sleep(1)
GPIO.wait_for_edge(pin,GPIO.RISING)

#####flash LED 10 times, with a random delay between each flash###
##for i_flash in range(24):
##    GPIO.output(18,1)
##    GPIO.output(pi2trig(10),1)
##    time.sleep(0.1)
##    GPIO.output(pi2trig(10),0)
##    GPIO.output(18,0)
##    time.sleep(randint(100,500)*0.001)

###remove fixation and instructions###
line1 = pygame.draw.line(screen, rect_black, (x_center-10, y_center), (x_center+10, y_center),4)
line2 = pygame.draw.line(screen, rect_black, (x_center, y_center-10), (x_center, y_center+10),4)
screen.fill(pygame.Color("black"))
##pygame.draw.rect(screen, rect_white , ((x_center-((rect_x+border_size)/2)),(y_center-((rect_y+border_size)/2)),rect_x+border_size,rect_y+border_size))
pygame.display.flip()

###start experiment###
exp_start = time.time()
GPIO.output(pi2trig(20),1)
time.sleep(0.5)
GPIO.output(pi2trig(255),0)
time.sleep(0.5)

###experiment###
for i_trial in range(len(all_trials)):
    ###wait for a random amount of time between tones###
    delay = ((randint(0,1000))*0.001)+stim_time
    delay_length.append(delay)
    if all_trials[i_trial][0] == 1:#square
        trial_img = pygame.image.load(nature_loc + 'Nature_' + str(all_trials[i_trial][1]) + '.tif')
        trial_img = pygame.transform.scale(trial_img,(rect_x,rect_y))
        trig_type.append(1)
        pic_num.append(all_trials[i_trial][1])
    elif all_trials[i_trial][0]  == 2:#triangle
        trial_img = pygame.image.load(urban_loc + 'Urban_' + str(all_trials[i_trial][1]) + '.tif')
        trial_img = pygame.transform.scale(trial_img,(rect_x,rect_y))
        trig_type.append(2)
        pic_num.append(all_trials[i_trial][1])
    elif all_trials[i_trial][0]  == 3:#square
        trial_img = pygame.image.load(face_loc + 'Face_' + str(all_trials[i_trial][1]) + '.tif')
        trial_img = pygame.transform.scale(trial_img,(rect_x,rect_y))
        trig_type.append(3)
        pic_num.append(all_trials[i_trial][1])
    elif all_trials[i_trial][0]  == 4:#triangle
        trial_img = pygame.image.load(scrambled_face_loc + 'Scrambled_Face_' + str(all_trials[i_trial][1]) + '.tif')
        trial_img = pygame.transform.scale(trial_img,(rect_x,rect_y))
        trig_type.append(4)
        pic_num.append(all_trials[i_trial][1])
    ###draw stim and send trigger### 
    trig_time.append(time.time() - exp_start)
    GPIO.output(pi2trig(int(all_trials[i_trial][0])),1)
    screen.fill(pygame.Color("black"))
##    pygame.draw.rect(screen, rect_white , ((x_center-((rect_x+border_size)/2)),(y_center-((rect_y+border_size)/2)),rect_x+border_size,rect_y+border_size))
    screen.blit(trial_img,((x_center-(trial_img.get_width()/2)),(y_center-(trial_img.get_height()/2))))
    pygame.display.flip()
    ###wait for a random amount of time and set the trigger back to zero###
    time.sleep(0.005)
    GPIO.output(pi2trig(255),0)
    ###now try and get a response###
    start_resp = time.time()
    edge_detect = GPIO.wait_for_edge(pin,GPIO.RISING, timeout = int(delay * 1000))
    if edge_detect is not None:  
        resp = time.time() - start_resp
        resp_time.append(resp)
        GPIO.output(pi2trig(int(all_trials[i_trial][0])+4),1)
        time.sleep(delay - resp)
        GPIO.output(pi2trig(255),0)
    else:
        resp_time.append(0)
        GPIO.output(pi2trig(255),0)
    screen.fill(pygame.Color("black"))
##    pygame.draw.rect(screen, rect_white , ((x_center-((rect_x+border_size)/2)),(y_center-((rect_y+border_size)/2)),rect_x+border_size,rect_y+border_size))
    pygame.display.flip()
    GPIO.output(pi2trig(int(all_trials[i_trial][0]+8)),1)
    time.sleep(1.0)
    GPIO.output(pi2trig(255),0)
    time.sleep(0.005)
    
##GoPro_LED_Flash(10)
###show the end screen###
GPIO.output(pi2trig(21),1)
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

the_list = [date, trig_type,pic_num,trig_time,delay_length,resp_time]
df_list = pd.DataFrame({i:pd.Series(value) for i, value in enumerate(the_list)})
df_list.columns = ['Date','Trigger_Type','Picture_Number','Trigger_Onset_Time','Trial_Delay','Response_Time']
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
