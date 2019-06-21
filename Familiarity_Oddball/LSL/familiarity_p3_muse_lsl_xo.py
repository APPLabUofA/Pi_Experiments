import time
import os
import sys
import random
import datetime
import numpy
import pygame
from pylsl import StreamInfo, StreamOutlet, local_clock
from collections import Counter

###FIRST DEFINE OUR PARTICIPANT NUMBER###
##part_num = '003'
##except_list = ['001']
##except_list.append(part_num)

text_file = open("/home/pi/Experiments/Familiarity_Oddball/Parts","r")
except_list = text_file.read().split(',')
part_num = except_list[0]
##with open('/home/pi/Experiments/Familiarity_Oddball/Participant_Number','r') as myfile:
##	part_num = myfile.read().replace('\n','')
##part_num= str(numpy.genfromtxt('/home/pi/Experiments/Familiarity_Oddball/Participant_Number', dtype='str'))
##except_list = str(numpy.genfromtxt('/home/pi/Experiments/Familiarity_Oddball/Exclude', dtype='str'))
##part_num = except_list[1:6]
#part_num= str(numpy.genfromtxt('/home/pi/Experiments/Familiarity_Oddball/Participant_Number', dtype='str'))

###setup variable related to pic and trial number here###
low_rate = 0.8
high_rate = 0.2

total_parts = 20
self_count = 5
fam_count = 5
place_count = 10
trials = 400


###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

###setup GPIO pins and initialise pygame###
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()
pygame.display.init()
pygame.mixer.init()

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h), pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)

###so, we need 2 master lists
###one that tells us if the current trial will be a standard or target
###another that will tell use if we need to show a self, family, or place image

###first we determine how many of each image we need
self_images = (numpy.zeros((2,total_parts*self_count)))+1
fam_images = (numpy.zeros((2,total_parts*fam_count)))+2
place_images = (numpy.zeros((2,total_parts*place_count)))+3

###now loop through and define our targets and standards###
for i_img in range(total_parts*self_count):
    if i_img < ((total_parts*self_count)*low_rate):
        self_images[1][i_img] = 1
    elif i_img >= ((total_parts*self_count)*low_rate):
        self_images[1][i_img] = 2

for i_img in range(total_parts*fam_count):
    if i_img < ((total_parts*fam_count)*low_rate):
        fam_images[1][i_img] = 1
    elif i_img >= ((total_parts*fam_count)*low_rate):
        fam_images[1][i_img] = 2

for i_img in range(total_parts*10):
    if i_img < ((total_parts*10)*low_rate):
        place_images[1][i_img] = 1
    elif i_img >= ((total_parts*10)*low_rate):
        place_images[1][i_img] = 2

###here we will combine our three matrices### 
image_order = numpy.concatenate((self_images,fam_images,place_images),axis = 1)

###convert them to a list, pair each of the elements, and then shuffle the order###
image_order = list(zip(image_order[0],image_order[1]))
random.shuffle(image_order)
image_order, trial_order = zip(*image_order)
image_order = list(image_order)
trial_order = list(trial_order)


block1 = []
block2 = []
block3 = []
block4 = []

for i in range(400):
    if i < 100:
        if i < 20:
            block1.append(2.0)
        elif i >= 20 and i < 100:
            block1.append(1.0)
    elif i >= 100 and i < 200:
        if i < 120:
            block2.append(2.0)
        elif i >= 120 and i < 200:
            block2.append(1.0)
    elif i >= 200 and i < 300:
        if i < 220:
            block3.append(2.0)
        elif i >= 220 and i < 300:
            block3.append(1.0)
    elif i >= 300 and i < 400:
        if i < 320:
            block4.append(2.0)
        elif i >= 320 and i < 400:
            block4.append(1.0)


random.shuffle(block1)
random.shuffle(block2)
random.shuffle(block3)
random.shuffle(block4)

trial_order_temp = []

for trial in range(len(trial_order)):
    if trial < 100:
        trial_order_temp.append(block1[trial])
    elif trial >= 100 and trial < 200:
        trial_order_temp.append(block2[trial-100])
    elif trial >= 200 and trial < 300:
        trial_order_temp.append(block3[trial-200])
    elif trial >= 300 and trial < 400:
        trial_order_temp.append(block4[trial-300])

trial_order = trial_order_temp



###define when we will have breaks###
break1 = int(trials*0.25)
break2 = int(trials*0.5)
break3 = int(trials*0.75)


###setup variables to record times###
trig_time   = []
delay_length = []
part_list = []
image_list = []
trig_time_lsl = []
#trig_time   = ["" for x in range(trials)]
#delay_length = ["" for x in range(trials)]
#part_list = ["" for x in range(trials)]
#image_list = ["" for x in range(trials)]
#image_type = ["" for x in range(trials)]

###setup our instruction screens###
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 20)
instructions_1 = myfont.render('Focus on the central fixation during the task.', True, white)
instructions_2 = myfont.render('Count in your head when you see a circle, DO NOT count when you see a cross.', True, white)
instructions_3 = myfont.render('Press the spacebar when you are ready to begin.', True, white)
break_screen_1 = myfont.render('Feel free to take a break at this time.', True, white)
break_screen_2 = myfont.render('Press the spacebar when you are ready to continue.', True, white)
done_1 = myfont.render('Great! You have finished the experiment!', True, white)
done_2 = myfont.render('Please let the experimenter know you have finished.', True, white)
done_3 = myfont.render('Press the spacebar to exit.', True, white)

###show our instructions, and wait for a response###
screen.blit(instructions_1,(x_center-((instructions_1.get_rect().width)/2),y_center + ((instructions_1.get_rect().height)*1)+10))
screen.blit(instructions_2,(x_center-((instructions_2.get_rect().width)/2),y_center + ((instructions_2.get_rect().height)*2)+10))
screen.blit(instructions_3,(x_center-((instructions_3.get_rect().width)/2),y_center + ((instructions_3.get_rect().height)*3)+10))
pygame.display.flip()
time.sleep(1)
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
pygame.draw.line(screen, (255, 255, 255), (x_center-30, y_center), (x_center+30, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-30), (x_center, y_center+30),4)
pygame.display.flip()
time.sleep(1)

###wait for button press to start experiment###
vid_start = time.time()
timestamp = local_clock()
time.sleep(1)
outlet.push_sample([3], timestamp)

for i_pic in range(trials):
    if i_pic in (break1, break2, break3):
        ###show the break screen, and wait for a response###
        screen.fill(pygame.Color("black")) 
        screen.blit(break_screen_1,(x_center-((break_screen_1.get_rect().width)/2),y_center + ((break_screen_1.get_rect().height)*1)+10))
        screen.blit(break_screen_2,(x_center-((break_screen_2.get_rect().width)/2),y_center + ((break_screen_2.get_rect().height)*2)+10))
        pygame.display.flip()
        time.sleep(1)
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
        pygame.draw.line(screen, (255, 255, 255), (x_center-30, y_center), (x_center+30, y_center),4)
        pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-30), (x_center, y_center+30),4)
        pygame.display.flip()
        time.sleep(1)

    ###wait for a random amount of time between images###
    delay = ((random.randint(0,500))*0.001)+1.00
    delay_length.append(delay)
    ###determine if the trial is a standrad or target###
    ###trial is a target###
    if trial_order[i_pic] == 2:
        
        pic_order_temp = 2
    ###change current part number to a string of the appropriate format###
        if int(part_num) > 9:
            part_order_temp = '0' + str(int(part_num))
        else:
            part_order_temp = '00' + str(int(part_num))

    ###now define our trigger to send with LSL###
        trigger = int(2)
        
    ###trial is a standard###
    elif trial_order[i_pic] == 1:
        
        pic_order_temp = 1
    ###pick a random number between 1 and our total number of participants###
        part_order_temp = '000'
    ###now define our trigger to send with LSL###
        trigger = int(1)
        
    ###record our part and image numbers###
    part_list.append(part_order_temp)
    image_list.append(pic_order_temp)
    if pic_order_temp > 9:
        pic_order_temp = str(pic_order_temp)
    else:
        pic_order_temp = '0' + str(pic_order_temp)
    #trial_img = pygame.image.load('/home/pi/Experiments/Familiarity_Oddball/Images/xo' + str(pic_order_temp) + '.png')
    print('/home/pi/Experiments/Familiarity_Oddball/Images/xo' + str(pic_order_temp) + '.png')                
    print(trigger)
    ###send triggers###
    timestamp = local_clock()
    outlet.push_sample([trigger], timestamp)
    trig_time.append(time.time() - vid_start)
    trig_time_lsl.append(timestamp)
    ###present image###
    screen.fill(pygame.Color("black")) 
    #screen.blit(trial_img,((x_center-(trial_img.get_width()/2.2)),(y_center-(trial_img.get_height()/2.2))))
    if pic_order_temp == "01":
        pygame.draw.line(screen, (255, 255, 255), (x_center-20, y_center+20), (x_center+20, y_center-20),5)
        pygame.draw.line(screen, (255, 255, 255), (x_center-20, y_center-20), (x_center+20, y_center+20),5)
    elif pic_order_temp == "02":
        print("circle")
        pygame.draw.circle(screen, (255, 255, 255), (x_center, y_center), 25, 3)
    pygame.display.flip()
    time.sleep(1.5)
    screen.fill(pygame.Color("black")) 
    pygame.draw.line(screen, (255, 255, 255), (x_center-30, y_center), (x_center+30, y_center),4)
    pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-30), (x_center, y_center+30),4)
    pygame.display.flip()
    ###wait for a random amount of time and set the trigger back to zero###
    time.sleep(delay)
    done = False
    counter = 0
    while not done and counter < delay:
        counter = counter + 1
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or pygame.K_BACKSPACE:
                    done = True
                    break
            elif event.type == pygame.QUIT:
                done = True
                break
        if done:
            break

os.remove("/home/pi/Experiments/Familiarity_Oddball/Stop_EEG.csv")
block_num = str(1)
filename    = "%s_%s_all_familiarity_p3_trigs_muse_xo"%(part_num,block_num)
while os.path.isfile(("/home/pi/Experiments/Familiarity_Oddball/Data/LSL/Muse/Muse_Recorded_Trig_Info_xo/%s.csv"%filename)) == True:
    block_num = str(int(block_num) + 1)
    filename    = "%s_%s_all_familiarity_p3_trigs_muse_xo"%(part_num,block_num)
    
filename_part = ("/home/pi/Experiments/Familiarity_Oddball/Data/LSL/Muse/Muse_Recorded_Trig_Info_xo/%s.csv"%filename)
numpy.savetxt(filename_part, (part_list,image_list,trial_order,trig_time,delay_length,trig_time_lsl), delimiter=',',fmt="%s")  

screen.fill(pygame.Color("black")) 
screen.blit(done_1,(x_center-((done_1.get_rect().width)/2),y_center + ((done_1.get_rect().height)*1)+10))
screen.blit(done_2,(x_center-((done_2.get_rect().width)/2),y_center + ((done_2.get_rect().height)*2)+10))
screen.blit(done_3,(x_center-((done_3.get_rect().width)/2),y_center + ((done_3.get_rect().height)*3)+10))
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
            elif event.key == pygame.K_BACKSPACE:
                key_pressed = 1
                pygame.display.quit()
                pygame.quit()
                sys.exit()
                            
time.sleep(5)

pygame.mouse.set_visible(0)
pygame.display.quit()
pygame.quit()    
sys.exit()
