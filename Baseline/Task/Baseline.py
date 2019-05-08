import time
import os
import sys
from random import randint
from random import shuffle
import datetime
import numpy
import pygame
import RPi.GPIO as GPIO
from pylsl import StreamInfo, StreamOutlet, local_clock

partnum = sys.argv[1]
device = sys.argv[2]
filename = sys.argv[3]
exp_loc = sys.argv[4]

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

###setup GPIO pins and initialise pygame###
GPIO.setmode(GPIO.BCM)
pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()
pygame.display.init()
pygame.mixer.init()

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

###set triggers to 0###
GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2

###FOR DEBUG###
#screen = pygame.display.set_mode((200,100),pygame.FULLSCREEN)
#x_center = 200/2
#y_center = 100/2
#####

black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)
pygame.mixer.music.load('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/high_tone.wav')

###define some other variables###
time_exp = 1
cond_order= randint(1,2)

###setup our initial instruction screens###
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 20)
instructions_open_1 = myfont.render('For this experiment you will perform four, three-minute segments with either your eyes open or closed.', True, white)
instructions_open_2 = myfont.render('For the first part of the experiment you will keep your eyes open and focus on the fixation cross.', True, white)
instructions_open_3 = myfont.render('You CAN blink during this time. Press the space bar when you are ready to begin.', True, white)

instructions_closed_1 = myfont.render('For this experiment you will perform four, three-minute segments with either your eyes open or closed.', True, white)
instructions_closed_2 = myfont.render('For the first part of the experiment you will keep your eyes closed.', True, white)
instructions_closed_3 = myfont.render('Press the space bar when you are ready to begin.', True, white)
instructions_closed_4 = myfont.render('Open your eyes when you hear a series of quick beeps through the headphones.', True, white)

###instructions for the eyes-closed condition###
open_complete_1 = myfont.render('Great! You have completed a three-minute segment!',True,white)
open_complete_2 = myfont.render('For the next segment, you will keep your eyes closed for three minutes.',True,white)
open_complete_3 = myfont.render('Open your eyes when you hear a series of quick beeps through the headphones.',True,white)
open_complete_4 = myfont.render('Press the space bar when you are ready to begin.',True,white)
open_complete_5 = myfont.render('Please keep your eyes closed during this time.',True,white)

###instructions for the eyes-open condition###
closed_complete_1 = myfont.render('Great! You have completed a three-minute segment!',True,white)
closed_complete_2 = myfont.render('For the next segment, you will keep your eyes open and focus on the fixation.',True,white)
closed_complete_3 = myfont.render('You CAN blink during this time. Press the space bar when you are ready.',True,white)

###completion instructions###
exp_complete_1 = myfont.render('Great! You have completed this experiment!',True,white)
exp_complete_2 = myfont.render('Please inform the experimenter you have finished.',True,white)

###send trigger for condition, 1 = open first, 2 = closed first###
timestamp = local_clock()
outlet.push_sample([int(cond_order)], timestamp)
GPIO.output(pi2trig('s',int(cond_order)),1)
time.sleep(0.1)
GPIO.output(pi2trig('s',int(cond_order)),0)

###show our instructions, and wait for a response###
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
if cond_order == 1:
    screen.blit(instructions_open_1,(x_center-((instructions_open_1.get_rect().width)/2),y_center + ((instructions_open_1.get_rect().height)*1)+10))
    screen.blit(instructions_open_2,(x_center-((instructions_open_2.get_rect().width)/2),y_center + ((instructions_open_2.get_rect().height)*2)+10))
    screen.blit(instructions_open_3,(x_center-((instructions_open_3.get_rect().width)/2),y_center + ((instructions_open_3.get_rect().height)*3)+10))
elif cond_order == 2:
    screen.blit(instructions_closed_1,(x_center-((instructions_closed_1.get_rect().width)/2),y_center + ((instructions_closed_1.get_rect().height)*1)+10))
    screen.blit(instructions_closed_2,(x_center-((instructions_closed_2.get_rect().width)/2),y_center + ((instructions_closed_2.get_rect().height)*2)+10))
    screen.blit(instructions_closed_3,(x_center-((instructions_closed_3.get_rect().width)/2),y_center + ((instructions_closed_3.get_rect().height)*3)+10))
    screen.blit(instructions_closed_4,(x_center-((instructions_closed_4.get_rect().width)/2),y_center + ((instructions_closed_4.get_rect().height)*4)+10))

pygame.display.flip()
key_pressed = 0
pygame.event.clear()
while key_pressed == 0:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            key_pressed = 1

for i_trial in range(1):
    ###present eyes open first###
    if cond_order == 1:
        ###now let's present our fixation cross and begin the 'eyes-open' condition###
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([11+i_trial], timestamp)
        GPIO.output(pi2trig('s',(11+i_trial)),1)
        time.sleep(0.1)
        GPIO.output(pi2trig('s',(11+i_trial)),0)
        screen.fill(pygame.Color("black")) 
        pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
        pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
        pygame.display.flip()
        time.sleep(time_exp)

        ###now display instructions for the 'eyes-closed' condition###
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([int(cond_order)], timestamp)
        GPIO.output(pi2trig('s',int(cond_order)),1)
        time.sleep(0.1)
        GPIO.output(pi2trig('s',int(cond_order)),0)
        screen.blit(open_complete_1,(x_center-((open_complete_1.get_rect().width)/2),y_center + ((open_complete_1.get_rect().height)*1)+10))
        screen.blit(open_complete_2,(x_center-((open_complete_2.get_rect().width)/2),y_center + ((open_complete_2.get_rect().height)*2)+10))
        screen.blit(open_complete_3,(x_center-((open_complete_3.get_rect().width)/2),y_center + ((open_complete_3.get_rect().height)*3)+10))
        screen.blit(open_complete_4,(x_center-((open_complete_4.get_rect().width)/2),y_center + ((open_complete_4.get_rect().height)*4)+10))
        pygame.display.flip()
        key_pressed = 0
        pygame.event.clear()
        while key_pressed == 0:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    key_pressed = 1

        ###remove the fixation cross and begin the 'eyes-closed' condition###
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([13+i_trial], timestamp)
        GPIO.output(pi2trig('s',(13+i_trial)),1)
        time.sleep(0.1)
        GPIO.output(pi2trig('s',(21+i_trial)),0)
        screen.fill(pygame.Color("black"))
        screen.blit(open_complete_5,(x_center-((open_complete_5.get_rect().width)/2),y_center + ((open_complete_5.get_rect().height))))
        pygame.display.flip()
        time.sleep(time_exp)

        ###play tones to signal to the participant that the task is over###
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([int(cond_order)], timestamp)
        GPIO.output(pi2trig('s',int(cond_order)),1)
        time.sleep(0.1)
        GPIO.output(pi2trig('s',int(cond_order)),0)
        for i_tone in range(3):
            pygame.mixer.music.play()
            time.sleep(0.5)

        if i_trial == 0:
            ###experiment is done,inform participant###
            timestamp = local_clock()
            outlet.push_sample([int(cond_order)], timestamp)
            GPIO.output(pi2trig('s',int(cond_order)),1)
            time.sleep(0.1)
            GPIO.output(pi2trig('s',int(cond_order)),0)
            screen.fill(pygame.Color("black"))
            screen.blit(exp_complete_1,(x_center-((exp_complete_1.get_rect().width)/2),y_center + ((exp_complete_1.get_rect().height)*1)+10))
            screen.blit(exp_complete_2,(x_center-((exp_complete_2.get_rect().width)/2),y_center + ((exp_complete_2.get_rect().height)*2)+10))
        elif i_trial != 0:
            ###now clear the screen and present instructions again for the 'eyes-open' condition###
            timestamp = local_clock()
            outlet.push_sample([int(cond_order)], timestamp)
            GPIO.output(pi2trig('s',int(cond_order)),1)
            time.sleep(0.1)
            GPIO.output(pi2trig('s',int(cond_order)),0)
            screen.fill(pygame.Color("black")) 
            pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
            pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
            screen.blit(closed_complete_1,(x_center-((closed_complete_1.get_rect().width)/2),y_center + ((closed_complete_1.get_rect().height)*1)+10))
            screen.blit(closed_complete_2,(x_center-((closed_complete_2.get_rect().width)/2),y_center + ((closed_complete_2.get_rect().height)*2)+10))
            screen.blit(closed_complete_3,(x_center-((closed_complete_3.get_rect().width)/2),y_center + ((closed_complete_3.get_rect().height)*3)+10))

        pygame.display.flip()
        key_pressed = 0
        pygame.event.clear()
        while key_pressed == 0:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    key_pressed = 1

    ###present eyes closed first###
    elif cond_order == 2:
        ###remove the fixation cross and begin the 'eyes-closed' condition###
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([13+i_trial], timestamp)
        GPIO.output(pi2trig('s',(13+i_trial)),1)
        time.sleep(0.1)
        GPIO.output(pi2trig('s',(13+i_trial)),0)
        screen.fill(pygame.Color("black"))
        screen.blit(open_complete_5,(x_center-((open_complete_5.get_rect().width)/2),y_center + ((open_complete_5.get_rect().height))))
        pygame.display.flip()
        time.sleep(time_exp)

        ###play tones to signal to the participant that the task is over###
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([int(cond_order)], timestamp)
        GPIO.output(pi2trig('s',int(cond_order)),1)
        time.sleep(0.1)
        GPIO.output(pi2trig('s',int(cond_order)),0)
        for i_tone in range(3):
            pygame.mixer.music.play()
            time.sleep(0.5)

        ###now let's present our fixation cross and begin the 'eyes-open' condition###
        screen.fill(pygame.Color("black")) 
        pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
        pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
        screen.blit(closed_complete_1,(x_center-((closed_complete_1.get_rect().width)/2),y_center + ((closed_complete_1.get_rect().height)*1)+10))
        screen.blit(closed_complete_2,(x_center-((closed_complete_2.get_rect().width)/2),y_center + ((closed_complete_2.get_rect().height)*2)+10))
        screen.blit(closed_complete_3,(x_center-((closed_complete_3.get_rect().width)/2),y_center + ((closed_complete_3.get_rect().height)*3)+10))
        pygame.display.flip()
        key_pressed = 0
        pygame.event.clear()
        while key_pressed == 0:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    key_pressed = 1

        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([11+i_trial], timestamp)
        GPIO.output(pi2trig('s',(11+i_trial)),1)
        time.sleep(0.1)
        GPIO.output(pi2trig('s',(11+i_trial)),0)
        screen.fill(pygame.Color("black")) 
        pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
        pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
        pygame.display.flip()
        time.sleep(time_exp)

        if i_trial == 0:
            timestamp = local_clock()
            outlet.push_sample([int(cond_order)], timestamp)
            GPIO.output(pi2trig('s',int(cond_order)),1)
            time.sleep(0.1)
            GPIO.output(pi2trig('s',int(cond_order)),0)
            screen.fill(pygame.Color("black"))
            screen.blit(exp_complete_1,(x_center-((exp_complete_1.get_rect().width)/2),y_center + ((exp_complete_1.get_rect().height)*1)+10))
            screen.blit(exp_complete_2,(x_center-((exp_complete_2.get_rect().width)/2),y_center + ((exp_complete_2.get_rect().height)*2)+10))
        elif i_trial != 0:
            ###now clear the screen and present instructions again for the 'eyes-open' condition###
            timestamp = local_clock()
            outlet.push_sample([int(cond_order)], timestamp)
            GPIO.output(pi2trig('s',int(cond_order)),1)
            time.sleep(0.1)
            GPIO.output(pi2trig('s',int(cond_order)),0)
            screen.fill(pygame.Color("black")) 
            pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
            pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
            screen.blit(open_complete_1,(x_center-((open_complete_1.get_rect().width)/2),y_center + ((open_complete_1.get_rect().height)*1)+10))
            screen.blit(open_complete_2,(x_center-((open_complete_2.get_rect().width)/2),y_center + ((open_complete_2.get_rect().height)*2)+10))
            screen.blit(open_complete_3,(x_center-((open_complete_3.get_rect().width)/2),y_center + ((open_complete_3.get_rect().height)*3)+10))
        
        pygame.display.flip()
        key_pressed = 0
        pygame.event.clear()
        while key_pressed == 0:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    key_pressed = 1

pygame.mouse.set_visible(0)

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

##numpy.savetxt(filename_part, (trig_type,trig_time, delay_length), delimiter=',',fmt="%s")

pygame.display.quit()
pygame.quit()
GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
