import time
import os
import sys
from random import randint
from random import shuffle
import datetime
import numpy
import pygame
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
pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()
pygame.display.init()
pygame.mixer.init()

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

###define the number of trials, and tones per trial###
trials = 1000
low_rate = 0.85
high_rate = 0.15
low_tone = numpy.zeros(int(trials*low_rate))
high_tone = numpy.ones(int(trials*high_rate))
low_tone_list = low_tone.tolist()
high_tone_list = high_tone.tolist()
tones = low_tone_list + high_tone_list
shuffle(tones)

sound_standard = '/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/1000hz_60ms_tone.wav'
sound_target = '/home/pi/research_experiments/Experiments/Stimuli/Sounds/Auditory_Oddball/1100hz_60ms_tone.wav'

###setup our instruction screens###
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
pygame.mixer.music.load(sound_standard)
volume_standard = pygame.mixer.music.get_volume()
volume_target = (pygame.mixer.music.get_volume())*0.1
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
pygame.mixer.music.load(sound_target)
volume_target = (pygame.mixer.music.get_volume())*0.06
pygame.mixer.music.set_volume(volume_target)
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
time.sleep(1)

for i_tone in range(len(tones)):
    if i_tone == (int(trials*0.50)):
        ###show the break screen, and wait for a response###
        timestamp = local_clock()
        outlet.push_sample([4], timestamp)
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
    ###wait for a random amount of time between tones###
    delay = 0.6
    delay_length.append(delay)
    if tones[i_tone] == 0:#low tone
        pygame.mixer.music.load(sound_standard)
        pygame.mixer.music.set_volume(volume_standard)
        trig_type.append(1)
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([1], timestamp)
        trig_time.append(time.time() - vid_start) 
    elif tones[i_tone] == 1:#high tone
        pygame.mixer.music.load(sound_target)
        pygame.mixer.music.set_volume(volume_target)
        trig_type.append(2)
        ###send triggers###
        timestamp = local_clock()
        outlet.push_sample([2], timestamp)
        trig_time.append(time.time() - vid_start) 
    ###playback tone###
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    ###wait for a random amount of time and set the trigger back to zero###
    time.sleep(delay)

###show the end screen###
timestamp = local_clock()
outlet.push_sample([5], timestamp)
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

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

numpy.savetxt(filename_part, (trig_type,trig_time,delay_length), delimiter=',',fmt="%s")

pygame.display.quit()
pygame.quit()   

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
