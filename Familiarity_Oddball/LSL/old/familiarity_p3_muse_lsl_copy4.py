import time
import os
import sys
import random
import datetime
import numpy
import pygame
from pylsl import StreamInfo, StreamOutlet, local_clock

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

total_parts = 6
self_count = 5
fam_count = 5
place_count = 10
trials = (self_count + fam_count + place_count)*total_parts

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

###define when we will have breaks###
break1 = int(trials*0.25)
break2 = int(trials*0.5)
break3 = int(trials*0.75)
break4 = int(trials*0.75)
break5 = int(trials*0.75)

###setup variables to record times###
trig_time   = []
delay_length = []
part_list = []
image_list = []
image_type = []
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
instructions_2 = myfont.render('Press the spacebar when you see your pictures, do not press the spacebar when you see other pictures.', True, white)
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
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()
time.sleep(1)

###wait for button press to start experiment###
vid_start = time.time()
timestamp = local_clock()
time.sleep(1)
outlet.push_sample([3], timestamp)

for i_pic in range(trials):
    if i_pic in (break1, break2, break3, break4 ,break5):
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
        pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
        pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
        pygame.display.flip()
        time.sleep(1)

    ###wait for a random amount of time between images###
    delay = ((random.randint(0,500))*0.001)+1.00
    delay_length.append(delay)
    ###determine if the trial is a standrad or target###
    ###trial is a target###
    if trial_order[i_pic] == 2:
    ###change current part number to a string of the appropriate format###
        if int(part_num) > 9:
            part_order_temp = '0' + str(int(part_num))
        else:
            part_order_temp = '00' + str(int(part_num))

    ###now define our trigger to send with LSL###
        trigger = int(2)
    ###trial is a standard###
    elif trial_order[i_pic] == 1:
    ###pick a random number between 1 and our total number of participants###
        part_order_temp = random.randint(1,total_parts)
        
        ###change part num to an appropriate format###
        if part_order_temp > 9:
            part_order_temp = '0' + str(int(part_order_temp))
        else:
            part_order_temp = '00' + str(int(part_order_temp))
    ###since standards are images from other parts, make sure we are not using the current part number###
        while part_order_temp in except_list:
            part_order_temp = random.randint(1,total_parts)
            ###change part num to an appropriate format###
            if part_order_temp > 9:
                part_order_temp = '0' + str(int(part_order_temp))
            else:
                part_order_temp = '00' + str(int(part_order_temp))

    ###now define our trigger to send with LSL###
        trigger = int(1)
    ###now determine the type of image, and image number,  we are showing###
    if image_order[i_pic] == 1:
        pic_order_temp = random.randint(1,self_count)
    elif image_order[i_pic] == 2:
        pic_order_temp = random.randint(1,fam_count)
    elif image_order[i_pic] == 3:
        pic_order_temp = random.randint(1,place_count)

    ###change part num to an appropriate format###
    if pic_order_temp > 9:
        pic_order_temp = str(int(pic_order_temp))
    else:
        pic_order_temp = '0' + str(int(pic_order_temp))

    ###now check to see what image type we will show###
    if image_order[i_pic] == 1:
        if os.path.exists('/home/pi/Experiments/Familiarity_Oddball/Images/' + part_order_temp + '_SFSS_' + pic_order_temp + '.jpg'):
            image_order_temp = 'SFSS'
        else:
            image_order_temp = 'SFBB'
    elif image_order[i_pic] == 2:
        if os.path.exists('/home/pi/Experiments/Familiarity_Oddball/Images/' + part_order_temp + '_FFSS_' + pic_order_temp + '.jpg'):
            image_order_temp = 'FFSS'
        else:
            image_order_temp = 'FFBB'
    elif image_order[i_pic] == 3:
        image_order_temp = 'P'

    ###record our part and image numbers###
    part_list.append(part_order_temp)
    image_list.append(pic_order_temp)
    image_type.append(image_order_temp)
    trial_img = pygame.image.load('/home/pi/Experiments/Familiarity_Oddball/Images/' + part_order_temp + '_' + image_order_temp + '_' + pic_order_temp + '.jpg')
    print('/home/pi/Experiments/Familiarity_Oddball/Images/' + part_order_temp + '_' + image_order_temp + '_' + pic_order_temp + '.jpg')
    print(trigger)
    ###send triggers###
    timestamp = local_clock()
    outlet.push_sample([trigger], timestamp)
    trig_time.append(time.time() - vid_start)
    trig_time_lsl.append(timestamp)
    ###present image###
    screen.fill(pygame.Color("black")) 
    screen.blit(trial_img,((x_center-(trial_img.get_width()/2)),(y_center-(trial_img.get_height()/2))))
    pygame.display.flip()
    time.sleep(1.5)
    screen.fill(pygame.Color("black")) 
    pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
    pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
    pygame.display.flip()
    ###wait for a random amount of time and set the trigger back to zero###
    time.sleep(delay)

time.sleep(5)
os.remove("/home/pi/Experiments/Familiarity_Oddball/Stop_EEG.csv")
filename    = "%s_all_familiarity_p3_trigs_muse"%(part_num)
filename_part = ("/home/pi/Experiments/Familiarity_Oddball/Data/LSL/Muse/Muse_Recorded_Trig_Info/%s.csv")%filename
numpy.savetxt(filename_part, (part_list,image_list,image_type,image_order,trial_order,trig_time,delay_length,trig_time_lsl), delimiter=',',fmt="%s")  

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
                
time.sleep(5)

pygame.mouse.set_visible(0)
pygame.display.quit()
pygame.quit()    
sys.exit()
