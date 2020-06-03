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

###setup GPIO pins and initialise pygame###
pi = pigpio.pi()
GPIO.setmode(GPIO.BCM)
pygame.init()
pygame.display.init()

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

###setup pins for each LCD###
trials = 100
lcd_freq = 17.0
dc = [0.1,6.0,50.0]
shutter_time = 5
baseline_time = 3

###setup pin for push button###
pin = 26
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

###number of trials###
##blocks = 12
##dc_range = [x for x in range(11)]
##dc_temp = dc_range
##for i_trials in range(blocks - 1):
####    dc_range = dc_range + dc_temp
##
##dc_range = np.ones(trials)*dc
##dc_range = dc_range.tolist()

all_trials = []
for i_dc in dc:
    dc_range = np.ones(trials)*i_dc
    dc_range = dc_range.tolist()
    
    ###determine face type for each trial###
    up_face = list(np.zeros(int(len(dc_range)/4.0))+1)
    down_face = list(np.zeros(int(len(dc_range)/4.0))+2)
    nature = list(np.zeros(int(len(dc_range)/4.0))+3)
    urban = list(np.zeros(int(len(dc_range)/4.0))+4)
    all_stims = up_face + down_face + nature + urban
    temp_trials = zip(dc_range,all_stims)
    all_trials = all_trials + temp_trials
    shuffle(all_trials)

###setup variables to record times###
trial_dc = []
trial_face = []
resp_time = []
resp_type = []
face_num = []

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

###variables for filenames and save locations###
partnum = '001'
device = 'Amp'
filename = 'Sequential_Shutter_Faces_Scenes'
exp_loc = 'Sequential_Shutter'
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

###define stimulus locations###
tone_resp= os.path.join('/home/pi/Experiments/Stimuli/Sounds/Auditory_Oddball', '1000hz_tone.wav')
eyes_closed = os.path.join('/home/pi/Experiments/Stimuli/Sounds', 'eyes_closed.wav')
eyes_open = os.path.join('/home/pi/Experiments/Stimuli/Sounds', 'eyes_open.wav')
face_loc = '/home/pi/Experiments/Stimuli/Images/Faces/'
nature_loc = '/home/pi/Experiments/Stimuli/Images/Nature/'
urban_loc = '/home/pi/Experiments/Stimuli/Images/Urban/'

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
instr = []
instr.append(myfont.render('You will be presented with a images at the start of each trial.', True, font_colour))
instr.append(myfont.render('The glasses may flash during each trial.', True, font_colour))
instr.append(myfont.render('Press ''Up'' for right-side-up faces, ''Down'' for up-side-down faces, ''Left'' for nature scenes, or ''Right'' for urban scenes.', True, font_colour))
instr.append(myfont.render('Press the space bar when you are ready to begin.', True, font_colour))
end_instr = myfont.render('Congratulations! You have finished the experiment! Contact the experimenter and press the space bar to close the task.', True, font_colour)

instr_size = []
for i_line in range(len(instr)):
    instr_size.append((x_center-((instr[i_line].get_rect().width)/2),y_center+((instr[i_line].get_rect().height))+200))

end_instr_size = (x_center-((end_instr.get_rect().width)/2),y_center+((end_instr.get_rect().height))+200)

###draw fixation and show our instructions###
pygame.draw.line(screen, fixation_colour, (x_center-fixation_length, y_center), (x_center+fixation_length, y_center),fixation_size)
pygame.draw.line(screen, fixation_colour, (x_center, y_center-fixation_length), (x_center, y_center+fixation_length),fixation_size)
for i_line in range(len(instr)):
    screen.blit(instr[i_line],instr_size[i_line])
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
    pygame.draw.rect(screen, white, (0, y_center+200, x_width, y_height),0)

###start experiment###
GPIO.output(pi2trig(1),1)
pygame.display.flip()
time.sleep(0.01)
GPIO.output(pi2trig(255),0)
temp_prev_face = 0
time.sleep(1)
start_exp = time.time()

###now we will run through the main task###

for i_trial in range(len(all_trials)):

    ###make DC 0% to allow for a baseline period###
    pi.hardware_PWM(18, lcd_freq, 0)
    GPIO.output(pi2trig(2),1)
    time.sleep(baseline_time/2.0)
    GPIO.output(pi2trig(255),0)
    time.sleep(baseline_time/2.0)

    ###show dc###
    ###trigs will be between 0:10 plus either 100 or 200, depending on face orientation###
    dc_trig = (dc.index(all_trials[i_trial][0])) + (int(all_trials[i_trial][1]) * 50)
    GPIO.output(pi2trig(dc_trig),1)
    pi.hardware_PWM(18, lcd_freq, all_trials[i_trial][0]*10000)
    trial_dc.append(int(all_trials[i_trial][0]))
    time.sleep(0.05)
    GPIO.output(pi2trig(255),0)

    ###show/update the current face type###
    if all_trials[i_trial][1] < 3:
        temp_face_num = randint(1,59)
        while temp_prev_face == temp_face_num:
            temp_face_num = randint(1,59)
        temp_prev_face = temp_face_num
        trial_face.append(all_trials[i_trial][1])
        face_num.append(temp_face_num)
        trial_img = pygame.image.load(face_loc + 'Face_' + str(temp_face_num) + '.tif')
        trial_img = pygame.transform.scale(trial_img,(rect_x,rect_y))
        if all_trials[i_trial][1] == 2:
            trial_img = pygame.transform.flip(trial_img,False,True)
    elif all_trials[i_trial][1] == 3:
        temp_face_num = randint(1,50)
        while temp_prev_face == temp_face_num:
            temp_face_num = randint(1,50)
        temp_prev_face = temp_face_num
        trial_face.append(all_trials[i_trial][1])
        face_num.append(temp_face_num)
        trial_img = pygame.image.load(nature_loc + 'Nature_' + str(temp_face_num) + '.tif')
        trial_img = pygame.transform.scale(trial_img,(rect_x,rect_y))
    elif all_trials[i_trial][1] == 4:
        temp_face_num = randint(1,50)
        while temp_prev_face == temp_face_num:
            temp_face_num = randint(1,50)
        temp_prev_face = temp_face_num
        trial_face.append(all_trials[i_trial][1])
        face_num.append(temp_face_num)
        trial_img = pygame.image.load(urban_loc + 'Urban_' + str(temp_face_num) + '.tif')
        trial_img = pygame.transform.scale(trial_img,(rect_x,rect_y))
    GPIO.output(pi2trig(dc_trig + 3),1)
    screen.blit(trial_img,((x_center-(trial_img.get_width()/2)),(y_center-(trial_img.get_height()/2))))
    pygame.display.flip()
    time.sleep(0.05)
    GPIO.output(pi2trig(255),0)
    time.sleep(0.05)

    ###wait for a response from the participant###
    key_pressed = 0
    pygame.event.clear()
    start_resp = time.time()
    wait_time = 0
    while key_pressed == 0 and wait_time <= shutter_time:
        ###update elapsed time###
        wait_time = time.time() - start_resp

        ###check for response###
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    GPIO.output(pi2trig(dc_trig + 6),1)
                    resp_time.append(time.time()-start_resp)
                    key_pressed = 'UP'
                    resp_type.append(key_pressed)
                elif event.key == pygame.K_DOWN:
                    GPIO.output(pi2trig(dc_trig + 9),1)
                    resp_time.append(time.time()-start_resp)
                    key_pressed = 'DOWN'
                    resp_type.append(key_pressed)
                elif event.key == pygame.K_LEFT:
                    GPIO.output(pi2trig(dc_trig + 12),1)
                    resp_time.append(time.time()-start_resp)
                    key_pressed = 'LEFT'
                    resp_type.append(key_pressed)
                elif event.key == pygame.K_RIGHT:
                    GPIO.output(pi2trig(dc_trig + 15),1)
                    resp_time.append(time.time()-start_resp)
                    key_pressed = 'RIGHT'
                    resp_type.append(key_pressed)
            pygame.event.pump()

    ###determine if we need to wait a bit more###
    if wait_time < shutter_time:
        time.sleep(shutter_time - wait_time)

    time.sleep(0.05)
    GPIO.output(pi2trig(255),0)
    time.sleep(0.05)
    
    ###remove face###
    screen.fill(pygame.Color("white"))
    GPIO.output(pi2trig(dc_trig + 18),1)
    pygame.display.flip()
    time.sleep(0.1)
    GPIO.output(pi2trig(255),0)
    time.sleep(0.5)

    ###check if a response was made###
    if key_pressed == 0:
        resp_time.append(0)
        resp_type.append('NO_RESP')
    
#####experiment is finished###
#####display instructions and reset triggers###
pi.hardware_PWM(18, lcd_freq, 0)
os.system(' sudo killall pigpiod')
screen.fill(pygame.Color("white"))
screen.blit(end_instr,end_instr_size)
GPIO.output(pi2trig(3),1)
time.sleep(0.1)
pygame.display.flip()
GPIO.output(pi2trig(255),0)
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

###save times for the main task###
while os.path.isfile("/home/pi/Experiments/" + exp_loc + "/Data/" + device + "/" + partnum + "_" + filename + ".csv") == True:
    if int(partnum) >= 9:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

filename_part = ("/home/pi/Experiments/" + exp_loc + "/Data/" + device + "/" + partnum + "_" + filename + ".csv")

the_list = [date, trial_dc, trial_face, face_num, resp_time, resp_type]
df_list = pd.DataFrame({i:pd.Series(value) for i, value in enumerate(the_list)})
df_list.columns = ['Date','Trial DC','Face Orientation','Face Number','Response_Time', 'Response Type']
df_list.to_csv(filename_part)

GPIO.output(pi2trig(255),0)
pygame.display.quit()
pygame.quit()
GPIO.cleanup()
