"""
Generate N170
=============

Face vs. house paradigm stimulus presentation for evoking present.

"""

from time import time
from optparse import OptionParser
from glob import glob
from random import choice, shuffle, randint
import os
import sys

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet, local_clock
import RPi.GPIO as GPIO

partnum = sys.argv[1]
device = sys.argv[2]
filename = sys.argv[3]
exp_loc = sys.argv[4]

###setup GPIO pins###
GPIO.setmode(GPIO.BCM)
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

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

GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

###determine how many faces we will be showing###
face_num = 10
face_repeat = 3

###this loop ensures that each face will be presented 10 times###
face_order = []
for i_loop in range(face_repeat):
    temp = np.zeros(10)
    for ii_loop in range(face_num):
        temp[ii_loop] = temp[ii_loop] + ii_loop + 1
    face_order  = face_order + temp.tolist()

###make lists of our different face types###
unfilt_face_list = np.zeros(int(face_num * face_repeat))+0
hfilt_face_list = np.zeros(int(face_num * face_repeat))+1
vfilt_face_list = np.zeros(int(face_num * face_repeat))+2

unfilt_face_list = unfilt_face_list.tolist()
hfilt_face_list = hfilt_face_list.tolist()
vfilt_face_list = vfilt_face_list.tolist()

###combine the above with our face_order###
###then combine everything into one list and shuffle###
unfilt_face_list = zip(unfilt_face_list,face_order)
hfilt_face_list = zip(hfilt_face_list,face_order)
vfilt_face_list = zip(vfilt_face_list,face_order)

image_type = unfilt_face_list + hfilt_face_list + vfilt_face_list
shuffle(image_type)

# Create markers stream outlet
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
outlet = StreamOutlet(info)

markernames = [1, 2, 3]
start = time()

# Set up trial parameters
n_trials = len(image_type)
iti = 0.9
soa = 0.2
jitter = 0.2

trial_resp = []
trial_type = []
trial_pic = []
trial_response = []
trial_position = []

# Setup trial list
trials = DataFrame(dict(image_type=image_type,
                        timestamp=np.zeros(n_trials)))

# Setup graphics
def load_image(filename):
    return visual.ImageStim(win=mywin, image=filename, pos=(0,0))

mywin = visual.Window([592,448], monitor='testMonitor', units='deg', winType='pygame',
                      fullscr=False)#[592,448],
mywin.mouseVisible = False
unfilt_faces = list(map(load_image, glob('/home/pi/research_experiments/Experiments/Stimuli/Faces/unfilt_face_*.tiff')))
hfilt_faces = list(map(load_image, glob('/home/pi/research_experiments/Experiments/Stimuli/Faces/hfilt_face_*.tiff')))
vfilt_faces = list(map(load_image, glob('/home/pi/research_experiments/Experiments/Stimuli/Faces/vfilt_face_*.tiff')))

unfilt_faces_copy = list(map(load_image, glob('/home/pi/research_experiments/Experiments/Stimuli/Faces/unfilt_face_*.tiff')))

fixation = visual.GratingStim(win=mywin, size = 0.2, pos = [0,0], sf = 0, rgb = [1,1,1])

instr1 = visual.TextStim(win=mywin,text='Focus on the central fixation.',pos=(0,-5))
instr2 = visual.TextStim(win=mywin,text='You will see unfiltered faces...',pos=(0,-5))
instr3 = visual.TextStim(win=mywin,text='...and filtered faces.',pos=(0,-5))
instr4 = visual.TextStim(win=mywin,text='You will select which face you saw...',pos=(0,-4))
instr5 = visual.TextStim(win=mywin,text='...using the numbers on the NumPad.',pos=(0,-5))
instr6 = visual.TextStim(win=mywin,text='Press the spacebar to begin.',pos=(0,-6))
break1 = visual.TextStim(win=mywin,text='Feel free to take a break.',pos=(0,-5))
break2 = visual.TextStim(win=mywin,text='Press the spacebar when you are ready to begin.',pos=(0,-6))
done1 = visual.TextStim(win=mywin,text='Congratulations! You have finished the experiment!',pos=(0,-5))
done2 = visual.TextStim(win=mywin,text='Please contact the experimenter.',pos=(0,-6))
number1 = visual.TextStim(win=mywin,text='1',pos=(-6,-0.25))
number2 = visual.TextStim(win=mywin,text='2',pos=(0,-0.25))
number3 = visual.TextStim(win=mywin,text='3',pos=(6,-0.25))
number4 = visual.TextStim(win=mywin,text='4',pos=(-6,5.75))
number5 = visual.TextStim(win=mywin,text='5',pos=(0,5.75))
number6 = visual.TextStim(win=mywin,text='6',pos=(6,5.75))
numbers = [number1,number2,number3,number4,number5,number6]

instr1.draw()
fixation.draw()
mywin.flip()
event.waitKeys()
instr2.draw()
image1 = choice(unfilt_faces)
image1.draw()
mywin.flip()
event.waitKeys()
instr3.draw()
image1 = choice(hfilt_faces)
image2 = choice(vfilt_faces)
for i_image in range(2):
    image1.draw()
    instr3.draw()
    mywin.flip()
    core.wait(1)
    image2.draw()
    instr3.draw()
    mywin.flip()
    core.wait(1)
event.waitKeys()
positions = [(-6,-3),(0,-3),(6,-3),(-6,3),(0,3),(6,3)]
pictures = np.random.permutation(10)
pictures = pictures[0:6]
image_resp = []
for i_pic in range(len(pictures)):
    image_resp.append(unfilt_faces_copy[pictures[i_pic]])
    image_resp[i_pic].size = 5
    image_resp[i_pic].pos= positions[i_pic]
    image_resp[i_pic].draw()
    numbers[i_pic].draw()        
instr4.draw()
instr5.draw()
mywin.flip()
event.waitKeys()
instr6.draw()
mywin.flip()
event.waitKeys()
timestamp = local_clock()
outlet.push_sample([15], timestamp)
GPIO.output(pi2trig('s',15),1)
core.wait(0.5)
GPIO.output(pi2trig('s',15),0)
core.wait(0.5)

block_count = 1
for ii in range(len(image_type)):
    if ii in [int(n_trials*0.10),int(n_trials*0.20),int(n_trials*0.30),int(n_trials*0.40),int(n_trials*0.50),int(n_trials*0.60),int(n_trials*0.70),int(n_trials*0.80),int(n_trials*0.90)]:
        break1.draw()
        break2.draw()
        timestamp = local_clock()
        outlet.push_sample([block_count * 100], timestamp)
        GPIO.output(pi2trig('r',block_count),1)
        block_count += 1
        mywin.flip()
        GPIO.output(pi2trig('r',15),0)
        core.wait(1)
        event.waitKeys()
    # Intertrial interval
    fixation.draw()
    timestamp = local_clock()
    outlet.push_sample([13], timestamp)
    GPIO.output(pi2trig('s',13),1)
    mywin.flip()
    core.wait((iti + np.random.rand() * jitter)/2)
    GPIO.output(pi2trig('s',15),0)
    core.wait((iti + np.random.rand() * jitter)/2)

    # Select and display image
    label = trials['image_type'].iloc[ii]
    label = int(image_type[ii][0])

    # Send marker
    image = []
    if markernames[label] == 1:
        image = unfilt_faces[int(image_type[ii][1])-1]
        image.draw()
        timestamp = local_clock()
        outlet.push_sample([markernames[label]], timestamp)
        GPIO.output(pi2trig('s',1),1)
    elif markernames[label] == 2:
        image = hfilt_faces[int(image_type[ii][1])-1]
        image.draw()
        timestamp = local_clock()
        outlet.push_sample([markernames[label]], timestamp)
        GPIO.output(pi2trig('s',2),1)
    elif markernames[label] == 3:
        image = vfilt_faces[int(image_type[ii][1])-1]
        image.draw()
        timestamp = local_clock()
        outlet.push_sample([markernames[label]], timestamp)
        GPIO.output(pi2trig('s',3),1)
    trial_type.append(markernames[label])
    trial_pic.append(int(image_type[ii][1]))
    mywin.flip()

    # offset
    core.wait(soa)
    GPIO.output(pi2trig('s',15),0)
    mywin.flip()
    core.wait((iti/2))

    ###response###
    positions = [(-6,-3),(0,-3),(6,-3),(-6,3),(0,3),(6,3)]
    pictures = np.random.permutation(10)
    pictures = pictures[0:6]
    current_pic = int(image_type[ii][1])-1
##    print(current_pic)
    if current_pic not in pictures:
        pictures[randint(0,5)] = current_pic
        
    pic_location = np.where(pictures == current_pic)
    pic_location = pic_location[0][0]+1
    image_resp = []
    for i_pic in range(len(pictures)):
        image_resp.append(unfilt_faces_copy[pictures[i_pic]])
        image_resp[i_pic].size = 5
        image_resp[i_pic].pos= positions[i_pic]
        image_resp[i_pic].draw()
        numbers[i_pic].draw()        

    timestamp = local_clock()
    outlet.push_sample([10], timestamp)
    GPIO.output(pi2trig('s',10),1)
    mywin.flip()
    core.wait(0.2)
    GPIO.output(pi2trig('s',15),0)

    keys = []
    while keys not in [['[1]'],['[2]'],['[3]'],['[4]'],['[5]'],['[6]']]:
##        print(keys)
        keys = event.waitKeys()

    keys = int(keys[0][1])
##    print(keys)

    if keys == pic_location:
        timestamp = local_clock()
        outlet.push_sample([11], timestamp)
        GPIO.output(pi2trig('s',11),1)
        trial_resp.append(11)
##        print('correct')
    elif keys != pic_location:
        timestamp = local_clock()
        outlet.push_sample([12], timestamp)
        GPIO.output(pi2trig('s',12),1)
        trial_resp.append(12)
##        print('incorrect')

    trial_response.append(keys)
    trial_position.append(pic_location)
    core.wait((iti/2))
    GPIO.output(pi2trig('s',15),0)
    core.wait(0.1)

    
    event.clearEvents()

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

np.savetxt(filename_part, (trial_resp,trial_type,trial_pic,trial_response,trial_position), delimiter=',',fmt="%s")

##core.wait(0.5)
done1.draw()
done2.draw()
mywin.flip()
event.waitKeys()
core.wait(1)

# Cleanup
if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:  
    core.wait(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    core.wait(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")

##core.wait(0.5)
GPIO.cleanup()
mywin.close()

