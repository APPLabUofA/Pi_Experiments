import time
import os
import random
import datetime
import numpy
from pylsl import StreamInfo, StreamOutlet, local_clock

###FIRST DEFINE OUR PARTICIPANT NUMBER###
part_num = '001'
except_list = ['002','003','004','005']
except_list.append(part_num)
#part_num= str(numpy.genfromtxt('/home/pi/Experiments/Familiarity_Oddball/Participant_Number', dtype='str'))

###setup variable related to pic and trial number here###
trials = 400
low_rate = 0.8
high_rate = 0.2

total_parts = 20
self_count = 5
fam_count = 5
place_count = 10

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

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

###setup variables to record times###
trig_time   = []
delay_length    = []
part_list = []
image_list = []

###wait for button press to start experiment###
vid_start = time.time()
timestamp = local_clock()
time.sleep(10)
outlet.push_sample([3], timestamp)

for i_pic in range(trials):
        ###wait for a random amount of time between images###
        delay = ((random.randint(0,500))*0.001)
        delay_length.append(delay)
        ###determine if the trial is a standrad or target###
        ###trial is a target###
        if trial_order[i_pic] == 2:
            part_order_temp = part_num

        ###now define our trigger to send with LSL###
            trigger = 2
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
            trigger = 1
        ###now determine the type of image, and image number,  we are showing###
        if image_order[i_pic] == 1:
            image_order_temp = 'S'
            pic_order_temp = random.randint(1,self_count)
        elif image_order[i_pic] == 2:
            image_order_temp = 'F'
            pic_order_temp = random.randint(1,fam_count)
        elif image_order[i_pic] == 3:
            image_order_temp = 'P'
            pic_order_temp = random.randint(1,place_count)

        ###change part num to an appropriate format###
        if pic_order_temp > 9:
            pic_order_temp = '0' + str(int(pic_order_temp))
        else:
            pic_order_temp = '00' + str(int(pic_order_temp))

        print('/home/pi/Experiments/Familiarity_Oddball/Images/' + part_order_temp + '_' + image_order_temp + '_' + pic_order_temp + '_image.jpg')
        print(trigger)
        ###record our part and image numbers###
        part_list.append(part_order_temp)
        image_list.append(pic_order_temp)
        ###triggers###
        timestamp = local_clock()
        outlet.push_sample([trigger], timestamp)
        trig_time.append(time.time() - vid_start)   
        ###wait for a random amount of time###
        time.sleep(delay)

filename = "%s_all_familiarity_p3_trigs_muse"%(part_num)
filename_part = ("/home/pi/Experiments/Familiarity_Oddball/Data/LSL/Muse/Muse_Recorded_Trig_Info/%s.csv")%filename

numpy.savetxt(filename_part, (part_list,image_list,image_order,trial_order,trig_time,delay_length), delimiter=',',fmt="%s")      

time.sleep(5)
os.remove("/home/pi/Experiments/Familiarity_Oddball/Stop_EEG.csv")
