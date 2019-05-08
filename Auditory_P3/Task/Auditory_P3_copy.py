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

###initialise pygame###
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

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)

###FOR DEBUG###
#screen = pygame.display.set_mode((200,100),pygame.RESIZABLE)
#x_center = 200/2
#y_center = 100/2
#####

###setup variables to record times###
vid_time  = []
trig_time   = []
trig_type = []
delay_length  = []

###set triggers to 0###
GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

###define the number of trials, and tones per trial###
trials = 10
low_rate = 0.8
high_rate = 0.2
low_tone = numpy.zeros(int(trials*low_rate))
high_tone = numpy.ones(int(trials*high_rate))
low_tone_list = low_tone.tolist()
high_tone_list = high_tone.tolist()
tones = low_tone_list + high_tone_list
shuffle(tones)

####setup our instruction screens###
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 20)
instructions1 = myfont.render('Focus on the central fixation.', True, white)
instructions2 = myfont.render('Press the spacebar when you hear the high pitched tones, do NOT press the spacebar for low pitched tones', True, white)
instructions3 = myfont.render('Press the spacebar to hear examples of the tones.', True, white)
example1 = myfont.render('This is an example of the low pitched tones.', True, white)
example2 = myfont.render('This is an example of the high pitched tones.', True, white)
example3 = myfont.render('Press the spacebar when you are ready to begin the experiment.', True, white)
break_screen = myfont.render('Feel free to take a break at this time. Press the Spacebar when you are ready to start.', True, white)
end_screen = myfont.render('Congratulations, you have finished the experiment! Please contact the experimenter.', True, white)

###show our instructions, and wait for a response###
screen.blit(instructions1,(x_center-((instructions1.get_rect().width)/2),y_center+((instructions1.get_rect().height)*1)+10))
screen.blit(instructions2,(x_center-((instructions2.get_rect().width)/2),y_center+((instructions2.get_rect().height)*2)+10))
screen.blit(instructions3,(x_center-((instructions3.get_rect().width)/2),y_center+((instructions3.get_rect().height)*3)+10))
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
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

###present examples of low tones###
screen.fill(pygame.Color("black")) 
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
screen.blit(example1,(x_center-((example1.get_rect().width)/2),y_center+((example1.get_rect().height)*1)+10))
pygame.display.flip()
pygame.mixer.music.load('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/low_tone.wav')
for i_tone in range(5):
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    time.sleep(1)

###pause for a bit###
screen.fill(pygame.Color("black")) 
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()
time.sleep(1)

###present examples of high tones###
screen.fill(pygame.Color("black")) 
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
screen.blit(example2,(x_center-((example2.get_rect().width)/2),y_center+((example2.get_rect().height)*1)+10))
pygame.display.flip()
pygame.mixer.music.load('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/high_tone.wav')
for i_tone in range(5):
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    time.sleep(1)

###pause for a bit###
screen.fill(pygame.Color("black")) 
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()
time.sleep(1)

###wait to start experiment###
screen.fill(pygame.Color("black")) 
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
screen.blit(example3,(x_center-((example3.get_rect().width)/2),y_center+((example3.get_rect().height)*1)+10))
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

screen.fill(pygame.Color("black")) 
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()
vid_start = time.time()
timestamp = local_clock()
outlet.push_sample([3], timestamp)
GPIO.output(pi2trig('s',3),1)
time.sleep(1)
GPIO.output(pi2trig('s',3),0)

for i_tone in range(len(tones)):
    if i_tone in (int(trials*0.25),int(trials*0.50),int(trials*0.75)):
        ###show the break screen, and wait for a response###
        timestamp = local_clock()
        outlet.push_sample([4], timestamp)
        GPIO.output(pi2trig('s',4),1)
        time.sleep(1)
        screen.fill(pygame.Color("black")) 
        screen.blit(break_screen,(x_center-((break_screen.get_rect().width)/2),y_center+10))
        pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
        pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
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
        screen.fill(pygame.Color("black")) 
        pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
        pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
        pygame.display.flip()
        time.sleep(1)
        GPIO.output(pi2trig('s',4),0)
    ###wait for a random amount of time between tones###
    delay = ((randint(0,500))*0.001)+1.00
    delay_length.append(delay)
    if tones[i_tone] == 0:#low tone
        pygame.mixer.music.load('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/low_tone.wav')
        trig_type.append(1)
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([1], timestamp)
        GPIO.output(pi2trig('s',1),1)
        trig_time.append(time.time() - vid_start) 
    elif tones[i_tone] == 1:#high tone
        pygame.mixer.music.load('/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/high_tone.wav')
        trig_type.append(2)
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([2], timestamp)
        GPIO.output(pi2trig('s',2),1)
        trig_time.append(time.time() - vid_start) 
    ###playback tone###
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    ###wait for a random amount of time and set the trigger back to zero###
    GPIO.output(pi2trig('s',15),0)
    GPIO.output(pi2trig('r',15),0)
    time.sleep(delay)

###show the end screen###
timestamp = local_clock()
outlet.push_sample([5], timestamp)
GPIO.output(pi2trig('s',5),1)
screen.fill(pygame.Color("black")) 
screen.blit(end_screen,(x_center-((end_screen.get_rect().width)/2),y_center+10))
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
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
GPIO.output(pi2trig('s',5),0)

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

numpy.savetxt(filename_part, (trig_type,trig_time,delay_length), delimiter=',',fmt="%s")

pygame.display.quit()
pygame.quit()
GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
