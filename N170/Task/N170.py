"""
Generate N170
=============

Face vs. house paradigm stimulus presentation for evoking present.

"""

from time import time
from optparse import OptionParser
from glob import glob
from random import choice, shuffle
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

directions = ['LEFT','RIGHT']
shuffle(directions)

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
face_repeat = 10

###this loop ensures that each face will be presented 10 times###
face_order = []
for i_loop in range(10):
    temp = np.zeros(10)
    for ii_loop in range(10):
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
trial_direction = []

# Setup trial list
trials = DataFrame(dict(image_type=image_type,
                        timestamp=np.zeros(n_trials)))

# Setup graphics
def load_image(filename):
    return visual.ImageStim(win=mywin, image=filename)

mywin = visual.Window([592,448], monitor='testMonitor', units='deg', winType='pygame',
                      fullscr=False)
mywin.mouseVisible = False
unfilt_faces = list(map(load_image, glob('/home/pi/research_experiments/Experiments/Stimuli/Faces/unfilt_face_*.tiff')))
hfilt_faces = list(map(load_image, glob('/home/pi/research_experiments/Experiments/Stimuli/Faces/hfilt_face_*.tiff')))
vfilt_faces = list(map(load_image, glob('/home/pi/research_experiments/Experiments/Stimuli/Faces/vfilt_face_*.tiff')))

fixation = visual.GratingStim(win=mywin, size = 0.2, pos = [0,0], sf = 0, rgb = [1,1,1])

instr1 = visual.TextStim(win=mywin,text='Focus on the central fixation.',pos=(0,-5))
instr2 = visual.TextStim(win=mywin,text='You will see complete faces...',pos=(0,-5))
instr3 = visual.TextStim(win=mywin,text='...and incomplete faces.',pos=(0,-5))
instr4 = visual.TextStim(win=mywin,text='Press ' + directions[0] +' if you think the face is male.',pos=(0,-4))
instr5 = visual.TextStim(win=mywin,text='Press ' + directions[1] +' if you think the face is female.',pos=(0,-5))
instr6 = visual.TextStim(win=mywin,text='Press the spacebar to begin.',pos=(0,-6))
break1 = visual.TextStim(win=mywin,text='Feel free to take a break.',pos=(0,-5))
break2 = visual.TextStim(win=mywin,text='Press the spacebar when you are ready to begin.',pos=(0,-6))
resp1 = visual.TextStim(win=mywin,text='Male (' + directions[0] +')',pos=(0,-1))
resp2 = visual.TextStim(win=mywin,text='Female (' + directions[1] +')',pos=(0,-2))
done1 = visual.TextStim(win=mywin,text='Congratulations! You have finished the experiment!',pos=(0,-5))
done2 = visual.TextStim(win=mywin,text='Please contact the experimenter.',pos=(0,-6))

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
instr4.draw()
instr5.draw()
instr6.draw()
mywin.flip()
event.waitKeys()
timestamp = local_clock()
outlet.push_sample([15], timestamp)
GPIO.output(pi2trig('s',15),1)
core.wait(0.5)
GPIO.output(pi2trig('s',15),0)
core.wait(0.5)

for ii in range(len(image_type)):#trials.iterrows():
    if ii in [int(n_trials*0.10),int(n_trials*0.20),int(n_trials*0.30),int(n_trials*0.40),int(n_trials*0.50),int(n_trials*0.60),int(n_trials*0.70),int(n_trials*0.80),int(n_trials*0.90)]:
        break1.draw()
        break2.draw()
        timestamp = local_clock()
        outlet.push_sample([14], timestamp)
        GPIO.output(pi2trig('s',14),1)
        mywin.flip()
        GPIO.output(pi2trig('s',15),0)
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
    resp1.draw()
    resp2.draw()
    mywin.flip()
    keys = event.waitKeys()
    while keys not in [['left'],['right']]:
        keys = event.waitKeys()

    if keys in [['left']]:
        timestamp = local_clock()
        outlet.push_sample([11], timestamp)
        GPIO.output(pi2trig('s',11),1)
        trial_resp.append(11)
    elif keys in [['right']]:
        timestamp = local_clock()
        outlet.push_sample([12], timestamp)
        GPIO.output(pi2trig('s',12),1)
        trial_resp.append(12)

    trial_direction.append(directions[0])
    core.wait((iti/2))
    GPIO.output(pi2trig('s',15),0)
    core.wait(0.1)

    
    event.clearEvents()

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

np.savetxt(filename_part, (trial_resp,trial_type,trial_pic,trial_direction), delimiter=',',fmt="%s")

core.wait(0.5)
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

core.wait(0.5)

GPIO.cleanup()
mywin.close()

