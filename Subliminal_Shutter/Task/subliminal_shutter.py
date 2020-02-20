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

###number of trials###
trials = 9
max_thresh_trials = 50

###specify when a break will occur%%%
breaks = [int(trials*(1/3.0))-1,int(trials*(2/3.0))-1]

###determine which duty cycles we will use for the three conditions###
vis_dc = 15
invis_dc = 0.0

###setup some variables for thresholding###
dc_incr = 0.1
crnt_dc = 5

correct_trials = []
incorrect_trials = []
correct_dc = []
incorrect_dc = []
correct_tracker = 0
incorrect_tracker = 0
thresh_thresh = 10

thresh = 1

###setup variables to record times###
trig_type = []
resp_time = []
resp_type = []

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

###variables for filenames and save locations###
partnum = '001'
device = 'Amp'
filename = 'Subliminal_Shutter'
exp_loc = filename
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

###define tones used for opening and closing eyes###
tone_resp= os.path.join('/home/pi/Experiments/Stimuli/Sounds/Auditory_Oddball', '1000hz_tone.wav')
eyes_closed = os.path.join('/home/pi/Experiments/Stimuli/Sounds', 'eyes_closed.wav')
eyes_open = os.path.join('/home/pi/Experiments/Stimuli/Sounds', 'eyes_open.wav')

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

###get our instructions ready###
myfont = pygame.font.SysFont('Times New Roman', 20)

thresh_instr = []
thresh_instr.append(myfont.render('First we must complete a threshold task.', True, white))
thresh_instr.append(myfont.render('This task will be similar to the main experiment.', True, white))
thresh_instr.append(myfont.render('Focus on the large fixation cross during the entire task.', True, white))
thresh_instr.append(myfont.render('At the start of each trial a prompt will tell you to close your eyes.', True, white))
thresh_instr.append(myfont.render('Another prompt will tell you to open your eyes and focus on the fixation cross.', True, white))
thresh_instr.append(myfont.render('After a few seconds you will again hear a prompt telling you to close your eyes.', True, white))
thresh_instr.append(myfont.render('When you hear a brief tone, press the ''Up'' arrow if you detected flashing, or the ''Down'' arrow if you did not detect any flashing.', True, white))
thresh_instr.append(myfont.render('Now, close your eyes and press the space bar when you are ready to begin.', True, white))

thresh_instr_size = []
for i_line in range(len(thresh_instr)):
    thresh_instr_size.append((x_center-((thresh_instr[i_line].get_rect().width)/2),y_center+((thresh_instr[i_line].get_rect().height))+200))

###setup our instruction screens###
instr = []
instr.append(myfont.render('Great! You finished the threshold task!', True, white))
instr.append(myfont.render('Before you start the main task, please contact the experimenter if you have any questions.', True, white))
instr.append(myfont.render('Focus on the large fixation cross during the entire task.', True, white))
instr.append(myfont.render('At the start of each trial a prompt will tell you to close your eyes.', True, white))
instr.append(myfont.render('Another prompt will tell you to open your eyes and focus on the fixation cross.', True, white))
instr.append(myfont.render('After a few seconds you will again hear a prompt telling you to close your eyes.', True, white))
instr.append(myfont.render('When you hear a brief tone, press the ''Up'' arrow if you detected flashing, or the ''Down'' arrow if you did not detect any flashing.', True, white))
instr.append(myfont.render('Now, close your eyes and press the space bar when you are ready to begin.', True, white))
end_instr = myfont.render('Congratulations! You have finished the experiment! Press the space bar to close the task.', True, white)

instr_size = []
for i_line in range(len(instr)):
    instr_size.append((x_center-((instr[i_line].get_rect().width)/2),y_center+((instr[i_line].get_rect().height))+200))

end_instr_size = (x_center-((end_instr.get_rect().width)/2),y_center+((end_instr.get_rect().height))+200)

###setup instructions for our breaks###
break_instr = myfont.render('Take a short break. Close your eyes and press spacebar when you are ready to continue.', True, white)

break_instr_size = (x_center-((break_instr.get_rect().width)/2),y_center+((break_instr.get_rect().height))+200)

###draw fixation and show our instructions###
pygame.draw.line(screen, (255, 255, 255), (x_center-200, y_center), (x_center+200, y_center),80)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-200), (x_center, y_center+200),80)
for i_line in range(len(thresh_instr)):
    screen.blit(thresh_instr[i_line],thresh_instr_size[i_line])
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
    pygame.draw.rect(screen, black, (0, y_center+200, x_width, y_height),0)

###remove instructions###
GPIO.output(pi2trig(41),1)
pygame.display.flip()
time.sleep(0.01)
GPIO.output(pi2trig(255),0)

###now we will run through the threshold task###
while thresh == 1:

    ###check to see if they got 1 consecutive correct trials###
    if correct_tracker == 1:
        correct_tracker = 0
        crnt_dc = crnt_dc - dc_incr
    ###check if they got the previous trial incorrect###
    elif len(incorrect_trials) > 0 and incorrect_trials[len(incorrect_trials)-1] == 1:
        crnt_dc = crnt_dc + dc_incr

    ###now show the maximum dc###
    GPIO.output(pi2trig(42),1)
    left_eye.ChangeDutyCycle(crnt_dc)
    right_eye.ChangeDutyCycle(crnt_dc)
    time.sleep(0.5)
    GPIO.output(pi2trig(255),0)
    
    ###play a tone to tell the participant to open their eyes###
    play_sound(eyes_open,43)
    time.sleep(1)

    ###wait some time###
    GPIO.output(pi2trig(44),1)
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    time.sleep(3)
    GPIO.output(pi2trig(45),1)
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)

    ###wait for a bit###
    time.sleep(0.5)

    ###play a tone to tell the participant to close their eyes###
    play_sound(eyes_closed,46)
    time.sleep(1)

    ###now show the minimum dc###
    GPIO.output(pi2trig(47),1)
    left_eye.ChangeDutyCycle(0)
    right_eye.ChangeDutyCycle(0)
    time.sleep(0.5)
    GPIO.output(pi2trig(255),0)

    ###play tone telling participant to respond###
    play_sound(tone_resp,48)

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
                    GPIO.output(pi2trig(49),1)
                    key_pressed = 'UP'
                    correct_trials.append(1)
                    incorrect_trials.append(0)
                    correct_dc.append(crnt_dc)
                    incorrect_dc.append(0)
                    correct_tracker += 1
                elif event.key == pygame.K_DOWN:
                    GPIO.output(pi2trig(50),1)
                    key_pressed = 'DOWN'
                    correct_trials.append(0)
                    incorrect_trials.append(1)
                    correct_dc.append(0)
                    incorrect_dc.append(crnt_dc)
                    correct_tracker = 0
                    incorrect_tracker += 1
            pygame.event.pump()
            
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    time.sleep(0.5)
    
    ###check if 50% of previous 10 trials are incorrect###
    if len(correct_trials) >= thresh_thresh:
        total_correct = [x for x in correct_trials[-thresh_thresh:] if x == 1]
        total_correct = np.sum(total_correct)
        total_incorrect = [x for x in incorrect_trials[-thresh_thresh:] if x == 1]
        total_incorrect = np.sum(total_incorrect)
        ###stop once we have a certain number of incorrect trials within a certain number of trials###
        if total_incorrect == int(thresh_thresh/2):
            thresh = 0
            play_sound(eyes_open,0)
            time.sleep(1)
    ###end thresholding if too many trials have passed###
    if len(correct_trials) == max_thresh_trials:
        thresh = 0
        total_correct = [x for x in correct_trials[-(thresh_thresh*2):] if x == 1]
        total_correct = np.sum(total_correct)
        total_incorrect = [x for x in incorrect_trials[-(thresh_thresh*2):] if x == 1]
        total_incorrect = np.sum(total_incorrect)
        play_sound(eyes_open,0)
        time.sleep(1)

###find mean dc for last 3 correct and incorrect trials###
mean_dc_correct = [x for x in correct_dc[-thresh_thresh:] if x > 0]
mean_dc_incorrect = [x for x in incorrect_dc[-thresh_thresh:] if x > 0]

mean_dc_correct = np.mean(mean_dc_correct)
mean_dc_incorrect = np.mean(mean_dc_incorrect)
    
###define the number of trials and conditions###
###we will try 3 duty cycle conditions (clearly visible, clearly not visiblbe, threshold)###

###determine which duty cycles we will use for the three conditions###
thresh_dc = np.mean([mean_dc_correct,mean_dc_incorrect])

###determine which trials will be which condition###
vis_trials_type = np.zeros(int(trials*(1.0/3.0)))+1
vis_trials_dc = np.zeros(int(trials*(1.0/3.0)))+vis_dc
vis_trials = zip(vis_trials_type,vis_trials_dc)

thresh_trials_type = np.zeros(int(trials*(1.0/3.0)))+2
thresh_trials_dc = np.zeros(int(trials*(1.0/3.0)))+thresh_dc
thresh_trials = zip(thresh_trials_type,thresh_trials_dc)

invis_trials_type = np.zeros(int(trials*(1.0/3.0)))+3
invis_trials_dc = np.zeros(int(trials*(1.0/3.0)))+invis_dc
invis_trials = zip(invis_trials_type,invis_trials_dc)

###now combine all trial types together and shuffle trial order###
all_trials = vis_trials + invis_trials + thresh_trials
shuffle(all_trials)

###draw fixation and show our instructions###
pygame.draw.line(screen, (255, 255, 255), (x_center-200, y_center), (x_center+200, y_center),80)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-200), (x_center, y_center+200),80)
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
    pygame.draw.rect(screen, black, (0, y_center+200, x_width, y_height),0)

###start experiment###
GPIO.output(pi2trig(51),1)
pygame.display.flip()
time.sleep(0.01)
GPIO.output(pi2trig(255),0)
start_exp = time.time()

###now we will run through the main task###
###each trial will go something like this###
###close eyes > start flash > tone to open eyes > watch flash for 10 seconds > beep to close eyes > response > stop flash###

for i_trial in range(len(all_trials)):

    ###now show the maximum dc###
    GPIO.output(pi2trig(int(all_trials[i_trial][0])*10+1),1)
    left_eye.ChangeDutyCycle(all_trials[i_trial][1])
    right_eye.ChangeDutyCycle(all_trials[i_trial][1])
    trig_type.append(int(all_trials[i_trial][0]))
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    
    ###wait for a bit###
    time.sleep(0.5)
    
    ###play a tone to tell the participant to open their eyes###
    play_sound(eyes_open,52)
    time.sleep(1)

    ###wait some time###
    GPIO.output(pi2trig(int(all_trials[i_trial][0])*10+2),1)
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    time.sleep(shutter_time)
    GPIO.output(pi2trig(int(all_trials[i_trial][0])*10+3),1)
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    time.sleep(0.5)

    ###play a tone to tell the participant to close their eyes###
    play_sound(eyes_closed,53)
    time.sleep(1)

    ###now show the minimum dc###
    GPIO.output(pi2trig(int(all_trials[i_trial][0])*10+4),1)
    left_eye.ChangeDutyCycle(0)
    right_eye.ChangeDutyCycle(0)
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    
    ###wait for a bit###
    time.sleep(0.5)

    ###play tone telling participant to respond###
    play_sound(tone_resp,54)
    time.sleep(0.01)

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
                    GPIO.output(pi2trig(int(all_trials[i_trial][0])*10+5),1)
                    resp_time.append(time.time()-start_time)
                    key_pressed = 'UP'
                    resp_type.append(key_pressed)
                elif event.key == pygame.K_DOWN:
                    GPIO.output(pi2trig(int(all_trials[i_trial][0])*10+6),1)
                    resp_time.append(time.time()-start_time)
                    key_pressed = 'DOWN'
                    resp_type.append(key_pressed)
            pygame.event.pump()
    time.sleep(0.01)
    GPIO.output(pi2trig(255),0)
    ###wait for a bit###
    time.sleep(1)

    ###take a break###
    if i_trial in breaks:
        screen.blit(break_instr,break_instr_size)
        GPIO.output(pi2trig(200),1)
        pygame.display.flip()
        time.sleep(0.01)
        GPIO.output(pi2trig(255),0)
        play_sound(eyes_open,201)
        time.sleep(1)
        key_pressed = 0
        while key_pressed == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        key_pressed = 1
                        GPIO.output(pi2trig(202),1)
                        time.sleep(0.01)
                        GPIO.output(pi2trig(255),0)
        pygame.draw.rect(screen, black, (0, y_center+200, x_width, y_height),0)
        pygame.display.flip()
        time.sleep(1)
    
#####experiment is finished###
#####display instructions and reset triggers###
left_eye.stop()
right_eye.stop()
play_sound(eyes_open,55)
screen.blit(end_instr,end_instr_size)
GPIO.output(pi2trig(56),1)
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

###save times for the threshold###
while os.path.isfile("/home/pi/Experiments/" + exp_loc + "/Data/" + device + "/" + partnum + "_" + filename + "threshold.csv") == True:
    if int(partnum) >= 9:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

filename_part = ("/home/pi/Experiments/" + exp_loc + "/Data/" + device + "/" + partnum + "_" + filename + "threshold.csv")

the_list = [date, correct_trials, correct_dc, incorrect_trials, incorrect_dc]
df_list = pd.DataFrame({i:pd.Series(value) for i, value in enumerate(the_list)})
df_list.columns = ['Date','Correct Trials','Correct DC','Incorrect Trials', 'Incorrect DC']
df_list.to_csv(filename_part)

###save times for the main task###
while os.path.isfile("/home/pi/Experiments/" + exp_loc + "/Data/" + device + "/" + partnum + "_" + filename + ".csv") == True:
    if int(partnum) >= 9:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

filename_part = ("/home/pi/Experiments/" + exp_loc + "/Data/" + device + "/" + partnum + "_" + filename + ".csv")

the_list = [date, thresh_dc, vis_dc, trig_type, resp_time, resp_type]
df_list = pd.DataFrame({i:pd.Series(value) for i, value in enumerate(the_list)})
df_list.columns = ['Date','Participant Threshold','Visible Threshold','Trigger_Type','Response_Time', 'Response Type']
df_list.to_csv(filename_part)

GPIO.output(pi2trig(255),0)
pygame.display.quit()
pygame.quit()
GPIO.cleanup()
