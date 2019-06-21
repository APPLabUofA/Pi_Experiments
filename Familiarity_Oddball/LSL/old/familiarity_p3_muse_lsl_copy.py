import time
import os
import random
import datetime
import numpy
import pygame
from pylsl import StreamInfo, StreamOutlet, local_clock

###FIRST DEFINE OUR PARTICIPANT NUMBER###
part_num = '001'

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
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)
img = pygame.image.load('/home/pi/Experiments/Familiarity_Oddball/Images/001_01_image.jpg')

###setup variable related to pic number here###
targ_range = 25
targ_pick = 20
stnd_range = 475
stnd_pick = 80
part_range = 20

###define when we will have breaks###
break1 = 50
break2 = 50
break3 = 50
break4 = 50
break5 = 50

###here we will randomly pick which target and standard images to use###
###part's own pics are targs, only using 20 of 25###
targ_list = random.sample(range(1, targ_range), targ_pick)

###also need to keep track of 

###pics of other parts are stnds, only using 80 of 475###
stnd_list = random.sample(range(1, stnd_range), stnd_pick)

###when picking stnds, need to pick from parts aside from current###
other_part = '00' + str(random.randint(1,part_range))
while int(part) == int(other_part):
    other_part = '00' + str(random.randint(1,part_range))

if int(other_part) > 9:
    other_part = '0' + str(int(other_part))
    
##### Define variables #####
partnum = "001"
stop_eeg = [0]
numpy.savetxt("/home/pi/Experiments/Familiarity_Oddball/Stop_EEG.csv", (stop_eeg), delimiter=',',fmt="%s")

###setup variables to record times###
vid_time    = []
trig_time   = []
trig_type   = []
delay_length    = []

###define the number of trials, and tones per trial###
trials = 100
low_rate = 0.8
high_rate = 0.2
standards = numpy.zeros(int(trials*low_rate))
targets = numpy.ones(int(trials*high_rate))
standards_list = standards.tolist()
targets_list = targets.tolist()
stim_order= standards_list + targets_list
random.shuffle(stim_order)

###here we will make our pic order match the shuffled stim_order variable###
pic_order = numpy.zeros(int(len(stim_order)))
part_order = numpy.zeros(int(len(stim_order)))

i_targ = 0
i_stnd = 0

for i_pic in range(len(stim_order)):
    if stim_order[i_pic] == 0:
        pic_order[i_pic] = stnd_list[i_stnd]
        i_stnd = i_stnd + 1
        part_order[i_pic] = random.randint(1,part_range)
        while int(part) == part_order[i_pic]:
            part_order[i_pic] = random.randint(1,part_range)
    elif stim_order[i_pic] == 1:
        pic_order[i_pic] = targ_list[i_targ]
        i_targ = i_targ + 1
        part_order[i_pic] = int(part)

###setup our instruction screens###
pygame.font.init()
myfont = pygame.font.SysFont('Times New Roman', 20)
instructions = myfont.render('Focus on the central fixation. Press the Spacebar when you are ready to start.', True, white)
break_screen = myfont.render('Feel free to take a break at this time. Press the Spacebar when you are ready to start.', True, white)

###show our instructions, and wait for a response###
screen.blit(instructions,(x_center-((instructions.get_rect().width)/2),y_center))
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

###wait for button press to start experiment###
vid_start = time.time()
timestamp = local_clock()
outlet.push_sample([3], timestamp)
time.sleep(1)

for i_pic in range(len(stim_order)):
    if i_pic in (break1, break2, break3, break4 ,break5):
        ###show the break screen, and wait for a response###
        screen.fill(pygame.Color("black")) 
        screen.blit(break_screen,(x_center-((instructions.get_rect().width)/2),y_center))
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
    else:
        ###wait for a random amount of time between tones###
        delay = ((random.randint(0,500))*0.001)+1.00
        delay_length.append(delay)
        if pic_order[i_pic] > 9:
            pic_order_temp = '0' + str(pic_order[i_pic])
        else:
            pic_order_temp = '00' + str(pic_order[i_pic])

        if part_order[i_pic] > 9:
            part_order_temp = '0' + str(part_order[i_pic])
        else:
            part_order_temp = '00' + str(part_order[i_pic])
            
        if stim_order[i_pic] == 0:#standard
            stnd_img = pygame.image.load('/home/pi/Experiments/Familiarity_Oddball/Images/' + part_order_temp + '_' + pic_order_temp + '_image.jpg')
            trig_type.append(1)
            ###send triggers###
            timestamp = local_clock()
            outlet.push_sample([1], timestamp)
            trig_time.append(time.time() - vid_start)   
            ###present image###
            screen.fill(pygame.Color("black")) 
            screen.blit(img,((x_center-(img.get_width()/2)),(y_center-(img.get_height()/2))))
            pygame.display.flip()
            time.sleep(0.5)
            screen.fill(pygame.Color("black")) 
            pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
            pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
            pygame.display.flip()
            ###wait for a random amount of time and set the trigger back to zero###
            time.sleep(delay)
        elif stim_order[i_pic] == 1:#target
            targ_img = pygame.image.load('/home/pi/Experiments/Familiarity_Oddball/Images/' + part_order_temp + '_' + pic_order_temp + '_image.jpg')
            trig_type.append(2)
            ###send triggers###
            timestamp = local_clock()
            outlet.push_sample([2], timestamp)
            trig_time.append(time.time() - vid_start)   
            ###present image###
            screen.fill(pygame.Color("black")) 
            screen.blit(img,((x_center-(img.get_width()/2)),(y_center-(img.get_height()/2))))
            pygame.display.flip()
            time.sleep(0.5)
            screen.fill(pygame.Color("black")) 
            pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
            pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
            pygame.display.flip()
            ###wait for a random amount of time and set the trigger back to zero###
            time.sleep(delay)

pygame.mouse.set_visible(0)
###save times###
while os.path.isfile("/home/pi/Experiments/Familiarity_Oddball/Data/LSL/Muse/Muse_Recorded_Trig_Info/%s_all_familiarity_p3_trigs_muse.csv"%(partnum)) == True:
    partnum = '00'+str(int(partnum)+1)
    if int(partnum) > 9:
        partnum = '0' + str(int(partnum))

filename    = "%s_all_familiarity_p3_trigs_muse"%(partnum)
filename_part = ("/home/pi/Experiments/Familiarity_Oddball/Data/LSL/Muse/Muse_Recorded_Trig_Info/%s.csv")%filename

numpy.savetxt(filename_part, (stim_order,part_order,pic_order,trig_time,delay_length), delimiter=',',fmt="%s")

pygame.display.quit()
pygame.quit()       

time.sleep(5)
stop_eeg = [1]
numpy.savetxt("/home/pi/Experiments/Familiarity_Oddball/Stop_EEG.csv", (stop_eeg), delimiter=',',fmt="%s")
