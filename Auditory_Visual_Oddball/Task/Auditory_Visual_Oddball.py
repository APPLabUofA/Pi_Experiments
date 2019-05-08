import os
import sys
from random import randint, shuffle
import time
import numpy as np
import pygame
import RPi.GPIO as GPIO
from pylsl import StreamInfo, StreamOutlet, local_clock
from six import string_types

partnum = sys.argv[1]
device = sys.argv[2]
filename = sys.argv[3]
exp_loc = sys.argv[4]

trials = 240
stim = 3
dist_count = 36

if stim == 3:
    num_prcnt = 0.33
    let_prcnt = 0.33
    tri_prcnt = 0.34
    hz1000_prcnt = 0.70
    hz2000_prcnt = 0.15
    dist_prcnt = 0.15
elif stim == 2:
    num_prcnt = 0.50
    let_prcnt = 0.50
    tri_prcnt = 0.0
    hz1000_prcnt = 0.70
    hz2000_prcnt = 0.15
    dist_prcnt = 0.15

###get GPIO pins ready###
GPIO.setmode(GPIO.BCM)
pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()
pygame.display.init()
pygame.mixer.init()
pygame.font.init()

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

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

###Setup our function to send triggers###
###trig_type is either 's' or 'r'###
###trig_num must be between 1-15###
def pi2trig(trig_type,trig_num):
    
    if trig_type == 's':
        pi_pins = [4,17,27,22]
    elif trig_type == 'r':       
        pi_pins = [5,6,13,19]
    
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

def fixation():
    pygame.draw.rect(screen, black, (x_center-30, y_center-30, 60, 60), 0)
    pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
    pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)

def cover_text():
    pygame.draw.rect(screen, black, (0, y_center+15, (x_center*2), y_center),0)

def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

def draw_text(stim):
    text = mystimfont.render(stim,True,white)
    stim_height = text.get_rect().height
    stim_width = text.get_rect().width
    stim_rect = (x_center-30, y_center-30, 60, 60)
    pygame.draw.rect(screen, black, stim_rect,0)
    screen.blit(text,(x_center-(stim_width/2),y_center-(stim_height/2)))
    pygame.display.update(stim_rect)
    return stim_rect

def draw_triangle(dims):
    pygame.draw.rect(screen, black, (x_center-30, y_center-30, 60, 60),0)
    triangle = pygame.draw.polygon(screen,white,dims, 0)
    pygame.display.update(triangle)
    return triangle
        
def send_trigger(lsl_trig, s_trig, s_on, r_trig, r_on):
    timestamp = local_clock()
    outlet.push_sample([lsl_trig], timestamp)
    GPIO.output(pi2trig('s',s_trig),s_on)
    GPIO.output(pi2trig('r',r_trig),r_on)
    
def get_resp_early(wait_time):
    start_time = pygame.time.get_ticks()
    key_pressed = 0
    pygame.event.clear()
    record_keys = 1
    while pygame.time.get_ticks() - start_time < wait_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and record_keys == 1:
                if event.key == pygame.K_a:
                    key_pressed = 1
                    record_keys = 0
                    send_trigger(7,7,1,15,0)
                elif event.key == pygame.K_l:
                    key_pressed = 2
                    record_keys = 0
                    send_trigger(8,8,1,15,0)
            pygame.event.pump()
    return key_pressed, record_keys

def get_resp(wait_time, record_keys):
    start_time = pygame.time.get_ticks()
    key_pressed = 0
    pygame.event.clear()
    while pygame.time.get_ticks() - start_time < wait_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and record_keys == 1:
                if event.key == pygame.K_a:
                    key_pressed = 1
                    record_keys = 0
                    send_trigger(9,15,0,9,1)
                elif event.key == pygame.K_l:
                    key_pressed = 2
                    record_keys = 0
                    send_trigger(10,15,0,10,1)
            pygame.event.pump()
    return key_pressed

def end_exp():
    pygame.mouse.set_visible(1)
    pygame.display.quit()
    GPIO.cleanup()
    pygame.quit()
    exit()

###setup the display screen and fixation###
rect_size = 100
rect_green = (0,255,0)
rect_red = (255,0,0)
triangle_size = 20
num_let_size = 40

##### Define variables #####
exp_start = []
trial_response = []
trial_response_early = []
trial_response_type = []
trial_visual_type = []
trial_sound_type = []
trial_visual_index = []
trial_sound_index = []
trial_visual_time = []
trial_sound_time = []
trial_stim_num = []
response_hand = ['LEFT','RIGHT']
response_keys = ['A','L']
response_order = zip(response_hand,response_keys)
shuffle(response_order)

###setup our visual stimuli###
mystimfont = pygame.font.SysFont('Times New Roman', num_let_size)

stim_numbers = ['2', '4', '6', '8']

stim_letters = ['a','e', 'c', 'u']

stim_triangles = [[(x_center-triangle_size,y_center+triangle_size),(x_center,y_center-triangle_size),(x_center+triangle_size,y_center+triangle_size)],
                  [(x_center-triangle_size,y_center-triangle_size),(x_center,y_center+triangle_size),(x_center+triangle_size,y_center-triangle_size)],
                  [(x_center-triangle_size,y_center),(x_center+triangle_size,y_center-triangle_size),(x_center+triangle_size,y_center+triangle_size)],
                  [(x_center-triangle_size,y_center-triangle_size),(x_center-triangle_size,y_center+triangle_size),(x_center+triangle_size,y_center)],]

stim_numbers_count = (np.zeros(int(trials*num_prcnt))+1).tolist()
stim_letters_count = (np.zeros(int(trials*let_prcnt))+2).tolist()
stim_triangles_count = (np.zeros(int(trials*tri_prcnt))+3).tolist()

all_visual_stims = stim_numbers_count + stim_letters_count + stim_triangles_count
shuffle(all_visual_stims)
all_visual_stims_copy = (np.zeros(len(all_visual_stims))).tolist()

for i_stim in range(len(all_visual_stims_copy)):
    all_visual_stims_copy[i_stim] = randint(0,3)

all_visual_stims = zip(all_visual_stims,all_visual_stims_copy)###first index is the stim type, second is the stim index###

###setup our sound stimuli###
sound_1000hz = os.path.join('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball', '1000hz_tone.wav')
sound_2000hz = os.path.join('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball', '2000hz_tone.wav')

count_1000hz = (np.zeros(int(trials*hz1000_prcnt))+1).tolist()
count_2000hz = (np.zeros(int(trials*hz2000_prcnt))+2).tolist()
natural_count = (np.zeros(int(trials*dist_prcnt))+3).tolist()

all_sound_stims = count_1000hz + count_2000hz + natural_count
shuffle(all_sound_stims)
all_sound_stims_copy = (np.zeros(len(all_sound_stims))).tolist()
used_dist_sounds = []
available_sounds = np.random.permutation(dist_count)
count = 0

for i_stim in range(len(all_sound_stims_copy)):
    if all_sound_stims[i_stim] == 1:
        all_sound_stims_copy[i_stim] = 0
    elif all_sound_stims[i_stim] == 2:
        all_sound_stims_copy[i_stim] = 1
    elif all_sound_stims[i_stim] == 3:
        crnt_sound = int(available_sounds[count])+1
        count += 1
##        crnt_sound = randint(1, dist_count)
##        while (crnt_sound in used_dist_sounds):
##            crnt_sound = randint(1, dist_count)
        all_sound_stims_copy[i_stim] = crnt_sound
        used_dist_sounds.append(crnt_sound)
        
all_sound_stims = zip(all_sound_stims,all_sound_stims_copy)

##sample_dist = randint(1,dist_count)
##while sample_dist in used_dist_sounds:
##    sample_dist = randint(1,dist_count)
##used_dist_sounds.append(sample_dist)
##sample_dist = sample_dist
sample_dist = randint(1,dist_count)

###set triggers to 0###
GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

###setup our instruction screens###
myfont = pygame.font.SysFont('Times New Roman', 20)
instr1 = myfont.render('Focus on the center of the screen.', True, white)
instr2 = myfont.render('You will be presented with auditory sounds...', True, white)
instr3 = myfont.render('...and you will be shown visual stimuli.', True, white)
instr4 = myfont.render('Ignore the auditory sounds, attend to the visual stimuli.', True, white)
instr5 = myfont.render('If you see a number, press ' + response_order[0][1] + ' with your ' + response_order[0][0] + ' hand.', True, white)
instr6 = myfont.render('If you see a letter, press ' + response_order[1][1] + ' with your ' + response_order[1][0] + ' hand.', True, white)
instr7 = myfont.render('If you see a triangle, DO NOT PRESS ANY KEYS.', True, white)
instr8 = myfont.render('Please let the experimenter know if you have questions.', True, white)
instr9 = myfont.render('Press the spacebar to begin the experiment.', True, white)
end1 = myfont.render('You have finished the experiment!', True, white)
end2 = myfont.render('Please contact the experimenter.', True, white)

instr1_size = (x_center-((instr1.get_rect().width)/2),y_center+((instr1.get_rect().height)*1)+10)
instr2_size = (x_center-((instr2.get_rect().width)/2),y_center+((instr2.get_rect().height)*1)+10)
instr3_size = (x_center-((instr3.get_rect().width)/2),y_center+((instr3.get_rect().height)*1)+30)
instr4_size = (x_center-((instr4.get_rect().width)/2),y_center+((instr4.get_rect().height)*1)+10)
instr5_size = (x_center-((instr5.get_rect().width)/2),y_center+((instr5.get_rect().height)*1)+10)
instr6_size = (x_center-((instr6.get_rect().width)/2),y_center+((instr6.get_rect().height)*1)+30)
instr7_size = (x_center-((instr7.get_rect().width)/2),y_center+((instr7.get_rect().height)*1)+50)
instr8_size = (x_center-((instr8.get_rect().width)/2),y_center+((instr8.get_rect().height)*1)+10)
instr9_size = (x_center-((instr9.get_rect().width)/2),y_center+((instr9.get_rect().height)*1)+30)
end1_size = (x_center-((end1.get_rect().width)/2),y_center+((end1.get_rect().height)*1)+10)
end2_size = (x_center-((end2.get_rect().width)/2),y_center+((end2.get_rect().height)*1)+30)

###show our instructions###
fixation()
screen.blit(instr1,instr1_size)
continue_exp(1)

fixation()
cover_text()
screen.blit(instr2,instr2_size)
pygame.display.flip()
for i_stim in range(3):
    play_sound(sound_1000hz)
    pygame.time.wait(1000)
    play_sound(sound_2000hz)
    pygame.time.wait(1000)
    play_sound(os.path.join('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Distractors', 'dist_' + str(sample_dist) + '.wav'))
    pygame.time.wait(1000)
continue_exp(0)

cover_text()
screen.blit(instr3,instr3_size)
pygame.display.flip()
for i_stim in range(4):
    draw_text(stim_numbers[i_stim])
    pygame.time.wait(1000)
    draw_text(stim_letters[i_stim])
    pygame.time.wait(1000)
    draw_triangle(stim_triangles[i_stim])
    pygame.time.wait(1000)
continue_exp(0)

cover_text()
fixation()
screen.blit(instr4,instr4_size)
continue_exp(1)

cover_text()
screen.blit(instr5,instr5_size)
draw_text(stim_numbers[randint(0,3)])
continue_exp(1)

cover_text()
screen.blit(instr6,instr6_size)
draw_text(stim_letters[randint(0,3)])
continue_exp(1)

cover_text()
screen.blit(instr7,instr7_size)
draw_triangle(stim_triangles[randint(0,3)])
continue_exp(1)

cover_text()
fixation()
screen.blit(instr8,instr8_size)
screen.blit(instr9,instr9_size)
continue_exp(1)

exp_start = pygame.time.get_ticks()
screen.fill(pygame.Color("black")) 
pygame.display.flip()
send_trigger(11,15,0,11,1)
pygame.time.wait(1000)

###main experiment###
for i_trial in range(1):#len(all_visual_stims)):
    delay = ((randint(0,500))+1500)
    ###present our sound, minus avg draw and flip time###
    trial_sound_time.append(pygame.time.get_ticks() - exp_start)
    if all_sound_stims[i_trial][0] == 1:###standards
        send_trigger(1,1,1,15,0)
        play_sound(sound_1000hz)
    elif all_sound_stims[i_trial][0] == 2:###targets
        send_trigger(2,2,1,15,0)
        play_sound(sound_2000hz)
    elif all_sound_stims[i_trial][0] == 3:###distractors
        send_trigger(3,3,1,15,0)
        play_sound(os.path.join('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Distractors', 'dist_' + str(int(all_sound_stims[i_trial][1])) + '.wav'))
    ###now wait and additional 150ms###
    trial_sound_type.append(all_sound_stims[i_trial][0])
    trial_sound_index.append(all_sound_stims[i_trial][1])
    pygame.time.wait(150)
    ###draw and flip our stimulus###
    trial_visual_time.append(pygame.time.get_ticks() - exp_start)
    if all_visual_stims[i_trial][0] == 1:###numbers
        send_trigger(4,15,0,4,1)
        stim_dims = draw_text(stim_numbers[all_visual_stims[i_trial][1]])
    elif all_visual_stims[i_trial][0] == 2:###letters
        send_trigger(5,15,0,5,1)
        stim_dims = draw_text(stim_letters[all_visual_stims[i_trial][1]])
    elif all_visual_stims[i_trial][0] == 3:###triangles
        send_trigger(6,15,0,6,1)
        stim_dims = draw_triangle(stim_triangles[all_visual_stims[i_trial][1]])
    ###wait for 200ms###
    trial_visual_type.append(all_visual_stims[i_trial][0])
    trial_visual_index.append(all_visual_stims[i_trial][1])
    resp, keys = get_resp_early(200)
    trial_response_early.append(resp)
    send_trigger(0,15,0,15,0)
    ###remove visual stimuli###
    screen.fill(pygame.Color("black"))
    pygame.display.update(stim_dims)
    ###now wait for a response###
    resp = get_resp(delay, keys)
    trial_response.append(resp)
    ###here we will record all our variables for this trial###
    trial_response_type.append(response_order[0][1])
    trial_stim_num.append(stim)

###show the end screen###
screen.blit(end1,end1_size)
screen.blit(end2,end2_size)
fixation()
send_trigger(12,12,1,15,0)
continue_exp(1)
pygame.mouse.set_visible(0)
send_trigger(0,15,0,15,0)

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

np.savetxt(filename_part, (trial_response, trial_response_early, trial_response_type, trial_visual_type, trial_sound_type,
                           trial_visual_index, trial_sound_index, trial_visual_time, trial_sound_time, trial_stim_num), delimiter=',',fmt="%s")

pygame.mouse.set_visible(1)
pygame.display.quit()
GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
    
pygame.time.wait(1000)
pygame.quit()
