import os
import sys
from random import randint, shuffle
import time
import numpy as np
import pygame
import RPi.GPIO as GPIO
from pylsl import StreamInfo, StreamOutlet, local_clock

partnum = sys.argv[1]
device = sys.argv[2]
filename = sys.argv[3]
exp_loc = sys.argv[4]

trials = 300

###get GPIO pins ready###
GPIO.setmode(GPIO.BCM)
pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()
pygame.display.init()
pygame.mixer.init()

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
sound_location = '/home/pi/research_experiments/Experiments/Stimuli/Sounds/Drums/'

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

##def display_break(time_left):
##    for i_time in range(time_left):
##        break1 = visual.TextStim(win=mywin,text='Feel free to have a break at this time.',pos=(0,-1))
##        break2 = visual.TextStim(win=mywin,text='You have ' + str(time_left - i_time) + ' seconds left.',pos=(0,-2))
##        break1.draw()
##        break2.draw()
##        mywin.flip()
##        core.wait(1)
##
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
                    
def send_trigger(lsl_trig, s_trig, s_on, r_trig, r_on):
    timestamp = local_clock()
    outlet.push_sample([lsl_trig], timestamp)
    GPIO.output(pi2trig('s',s_trig),s_on)
    GPIO.output(pi2trig('r',r_trig),r_on)

def fixation():
    screen.fill(pygame.Color("black"))
    pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
    pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)

def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

##### Define variables #####
exp_start = []
trial_type = []
trial_delay = []
trial_sound_order = []

###setup our sound stimuli###
low_rate = 0.8
high_rate = 0.2
low_tone = np.zeros(int(trials*low_rate))
high_tone = np.ones(int(trials*high_rate))
low_tone_list = low_tone.tolist()
high_tone_list = high_tone.tolist()
tones = low_tone_list + high_tone_list
shuffle(tones)

##bird_sounds = list(map(load_sounds, glob('/home/pi/Experiments/Auditory_Bird_Oddball/Task/Sounds/*.mp3')))
##shuffle(bird_sounds)
##
##target_sound = bird_sounds[randint(0,len(bird_sounds))]
##standard_sound = bird_sounds[randint(0,len(bird_sounds))]
##while standard_sound == target_sound:
##    standard_sound = bird_sounds[randint(0,len(bird_sounds))]
drum_sounds = os.listdir(sound_location)

sound_order = randint(0,len(drum_sounds)-1)
target_sound = sound_order
target_file = str(sound_location + drum_sounds[sound_order])
while target_file == str(sound_location + drum_sounds[sound_order]):
    sound_order = randint(0,len(drum_sounds)-1)

standard_sound = sound_order 
standard_file = str(sound_location + drum_sounds[sound_order])

print(drum_sounds)
print(target_file)
print(standard_file)

###set triggers to 0###
GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

###setup our instruction screens###
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 20)
instr1 = myfont.render('Focus on the central fixation.', True, white)
instr2 = myfont.render('You will be presented with drums', True, white)
instr3 = myfont.render('Press spacebar to this drum...', True, white)
instr4 = myfont.render('DO NOT press spacebar to this drum...', True, white)
instr5 = myfont.render('Please let the experimenter know if you have questions.', True, white)
instr6 = myfont.render('Press the spacebar to begin the experiment.', True, white)
end1 = myfont.render('You have finished the experiment!', True, white)
end2 = myfont.render('Please contact the experimenter.', True, white)

instr1_size = (x_center-((instr1.get_rect().width)/2),y_center+((instr1.get_rect().height)*1)+10)
instr2_size = (x_center-((instr2.get_rect().width)/2),y_center+((instr2.get_rect().height)*1)+30)
instr3_size = (x_center-((instr3.get_rect().width)/2),y_center+((instr3.get_rect().height)*1)+10)
instr4_size = (x_center-((instr4.get_rect().width)/2),y_center+((instr4.get_rect().height)*1)+10)
instr5_size = (x_center-((instr5.get_rect().width)/2),y_center+((instr5.get_rect().height)*1)+10)
instr6_size = (x_center-((instr6.get_rect().width)/2),y_center+((instr6.get_rect().height)*1)+30)
end1_size = (x_center-((end1.get_rect().width)/2),y_center+((end1.get_rect().height)*1)+10)
end2_size = (x_center-((end2.get_rect().width)/2),y_center+((end2.get_rect().height)*1)+30)

###show our instructions###
fixation()
screen.blit(instr1,instr1_size)
screen.blit(instr2,instr2_size)
continue_exp(1)

fixation()
screen.blit(instr3,instr3_size)
pygame.display.flip()
for i_stim in range(5):
    play_sound(target_file)
    pygame.time.wait(1000)
continue_exp(0)

fixation()
screen.blit(instr4,instr4_size)
pygame.display.flip()
for i_stim in range(5):
    play_sound(standard_file)
    pygame.time.wait(1000)
continue_exp(0)

fixation()
screen.blit(instr5,instr5_size)
screen.blit(instr6,instr6_size)
continue_exp(1)

exp_start = pygame.time.get_ticks()
fixation()
pygame.display.flip()
send_trigger(int(sound_order),int(sound_order),1,15,0)
pygame.time.wait(1000)
send_trigger(0,15,0,15,0)
pygame.time.wait(1000)
start_exp = pygame.time.get_ticks()

for i_trial in range(len(tones)):
    delay = ((randint(0,500))+1000)
    trial_delay.append(delay)
    ###present our sound###
    if tones[i_trial] == 0:###standard
        trial_sound_order.append(standard_sound)
        trial_type.append(1)
        send_trigger(1,1,1,0,0)
        play_sound(standard_file)
    elif tones[i_trial] == 1:###target
        trial_sound_order.append(target_sound)
        trial_type.append(2)
        send_trigger(2,2,1,0,0)
        play_sound(target_file)
    pygame.time.wait(int(delay/2))
    send_trigger(0,15,0,15,0)
    pygame.time.wait(int(delay/2))

###show the end screen###
print((pygame.time.get_ticks() - start_exp)/1000)
fixation()
screen.blit(end1,end1_size)
screen.blit(end2,end2_size)
timestamp = local_clock()
outlet.push_sample([500], timestamp)
GPIO.output(pi2trig('r',5),1)
continue_exp(1)
GPIO.output(pi2trig('r',15),0)

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

np.savetxt(filename_part, (trial_type,trial_delay,trial_sound_order), delimiter=',',fmt="%s")

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
