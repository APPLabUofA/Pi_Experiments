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
import numpy.matlib
from pandas import DataFrame
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet, local_clock
import RPi.GPIO as GPIO

partnum = sys.argv[1]
device = sys.argv[2]
filename = sys.argv[3]
exp_loc = sys.argv[4]

faceNum = 3
trials_per = 6
response_keys = [['y'],['n']]

# Create markers stream outlet
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
outlet = StreamOutlet(info)

start = time()

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

def load_image(filename):
    return visual.ImageStim(win=mywin, image=filename)

def send_trigger(lsl_trig, s_trig, s_on, r_trig, r_on):
    timestamp = local_clock()
    outlet.push_sample([lsl_trig], timestamp)
    GPIO.output(pi2trig('s',s_trig),s_on)
    GPIO.output(pi2trig('r',r_trig),r_on)

GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)   

###first let's setup our trials, ensuring everything is counterbalanced###
trials_CueProbeAnswer=(
(numpy.matlib.repmat([0, 0, 1], trials_per, 1)).tolist() +
(numpy.matlib.repmat([0, 1, 0.5], trials_per/2, 1)).tolist() +
(numpy.matlib.repmat([0, 2, 0.5], trials_per/2, 1)).tolist() +
(numpy.matlib.repmat([0, -1, 0], trials_per, 1)).tolist() +
(numpy.matlib.repmat([1, 1, 1], trials_per, 1)).tolist() +
(numpy.matlib.repmat([1, 0, 0.5], trials_per/2, 1)).tolist() +
(numpy.matlib.repmat([1, 2, 0.5], trials_per/2, 1)).tolist() +
(numpy.matlib.repmat([1, -1, 0], trials_per, 1)).tolist() +
(numpy.matlib.repmat([2, 2, 1], trials_per, 1)).tolist() +
(numpy.matlib.repmat([2, 0, 0.5], trials_per/2, 1)).tolist() +
(numpy.matlib.repmat([2, 1, 0.5], trials_per/2, 1)).tolist() +
(numpy.matlib.repmat([2, -1, 0], trials_per, 1)).tolist())

shuffle(trials_CueProbeAnswer)

faceIDs = (np.array([1,2,3,4,5,6,7,8,9,10])-1).tolist()

###setup which faces not to use on the first trial###
usedFaceIDs = np.random.permutation(10)[0:4]
usedFaceIDs = usedFaceIDs
usedFaceIDs = usedFaceIDs.tolist()

###determine is we want to match the gender of the cued and probe faces###
###can set this to 0 to make the task more difficult###
matchGender = 1
womenIDs = np.array([1, 3, 4, 8, 10])-1;
menIDs = np.array([2, 5, 6, 7, 9])-1;

###Set up trial parameters###
n_trials = len(trials_CueProbeAnswer)
iti = 0.9
soa = 0.2
jitter = 0.2

###variables to record data###
trial_resp = []
trial_learnFaces = []
trial_cueOrder = []
trial_probeFace = []
trial_probeType = []
trial_correctResponse = []
trial_usedFaceIDs = []
trial_faceChoices = []

###Setup graphics###
mywin = visual.Window([592,448], monitor='testMonitor', units='deg', winType='pygame',fullscr=False)
mywin.mouseVisible = False
unfilt_faces = list(map(load_image, glob('/home/pi/research_experiments/Experiments/Stimuli/Faces/unfilt_face_*.tiff')))

fixation = visual.GratingStim(win=mywin, size = 0.2, pos = [0,0], sf = 0, rgb = [1,1,1])
fixation_cue = visual.GratingStim(win=mywin, size = 0.2, pos = [0,0], sf = 0, rgb = [0,0,1])

instr1 = visual.TextStim(win=mywin,text='You will be shown 3 faces...',pos=(0,-4))
instr2 = visual.TextStim(win=mywin,text='...one after the other on every trial.',pos=(0,-5))
instr3 = visual.TextStim(win=mywin,text='Please remember the faces and...',pos=(0,-4))
instr4 = visual.TextStim(win=mywin,text='... the order in which they were shown.',pos=(0,-5))
instr5 = visual.TextStim(win=mywin,text='After a short delay, you will see the...',pos=(0,-4))
instr6 = visual.TextStim(win=mywin,text='...number 1, 2, or 3 on the screen.',pos=(0,-5))
instr7 = visual.TextStim(win=mywin,text='This number prompts you to remember the...',pos=(0,-4))
instr8 = visual.TextStim(win=mywin,text='...1st, 2nd, or 3rd face.',pos=(0,-5))
instr9 = visual.TextStim(win=mywin,text='After a brief delay, you will be shown another face...',pos=(0,-4))
instr10 = visual.TextStim(win=mywin,text='...and will press ''Y'' or ''N'' to indicate if this face...',pos=(0,-5))
instr11= visual.TextStim(win=mywin,text='...corresponds to the face you were asked to remember.',pos=(0,-6))
instr12= visual.TextStim(win=mywin,text='Please respond as quickly and as accurately as you can.',pos=(0,-5))
instr13= visual.TextStim(win=mywin,text='Let the experimenter know if you have questions.',pos=(0,-4))
instr14= visual.TextStim(win=mywin,text='Press the spacebar when you are ready to begin.',pos=(0,-5))
break1 = visual.TextStim(win=mywin,text='Feel free to take a break.',pos=(0,-4))
break2 = visual.TextStim(win=mywin,text='Press the spacebar when you are ready to begin.',pos=(0,-5))
trial_start = visual.TextStim(win=mywin,text='Remember faces and their order.',pos=(0,0))
done1 = visual.TextStim(win=mywin,text='Congratulations! You have finished the experiment!',pos=(0,-4))
done2 = visual.TextStim(win=mywin,text='Please contact the experimenter.',pos=(0,-5))
cues = list([visual.TextStim(win=mywin,text='1',pos=(0,0)), visual.TextStim(win=mywin,text='2',pos=(0,0)), visual.TextStim(win=mywin,text='3',pos=(0,0))])

instr1.draw()
instr2.draw()
fixation.draw()
mywin.flip()
core.wait(1)
event.waitKeys()

for i_image in range(3):
    instr3.draw()
    instr4.draw()
    unfilt_faces[usedFaceIDs[i_image]].draw()
    mywin.flip()
    core.wait(1)
    instr3.draw()
    instr4.draw()
    fixation.draw()
    mywin.flip()
    core.wait(1)
core.wait(1)
event.waitKeys()

instr5.draw()
instr6.draw()
fixation_cue.draw()
mywin.flip()
core.wait(1.5)
instr5.draw()
instr6.draw()
cues[1].draw()
mywin.flip()
core.wait(1)
event.waitKeys()

instr7.draw()
instr8.draw()
cues[1].draw()
mywin.flip()
core.wait(1)
event.waitKeys()

instr9.draw()
instr10.draw()
instr11.draw()
unfilt_faces[usedFaceIDs[3]].draw()
mywin.flip()
core.wait(1)
event.waitKeys()

instr12.draw()
unfilt_faces[usedFaceIDs[3]].draw()
mywin.flip()
core.wait(1)
event.waitKeys()

instr13.draw()
instr14.draw()
mywin.flip()
core.wait(1)
event.waitKeys()

timestamp = local_clock()
outlet.push_sample([15], timestamp)
GPIO.output(pi2trig('r',15),1)
core.wait(0.5)
GPIO.output(pi2trig('r',15),0)
core.wait(0.5)


###main experiment###
for i_trial in range((trials_per * 6)+((trials_per/2) * 6)):
    print((trials_per * 6)+((trials_per/2) * 6))
    print(usedFaceIDs)
    ###determine which faces we can show on this trial###
    faceChoices = list(set(faceIDs).symmetric_difference(set(usedFaceIDs)))
    shuffle(faceChoices)
    print(faceChoices)
    learnFaces = faceChoices[0:faceNum]
    print(learnFaces)

    ###this refers to the location participants must recall###
    cueOrder = int(trials_CueProbeAnswer[i_trial][0])
    print(cueOrder)

    ###this refers to the face participants must recall###
    probeType = int(trials_CueProbeAnswer[i_trial][1])
    print(probeType)

    ###present brief instructions and fixation###
    trial_start.draw()
    send_trigger(1, 1, 1, 15, 0)
    mywin.flip()
    core.wait(0.5)
    
    fixation.draw()
    send_trigger(2, 15, 0, 2, 1)
    mywin.flip()
    core.wait(0.3)
    
    ###now present each face###
    for i_face in range(3):
        unfilt_faces[learnFaces[i_face]].draw()
        send_trigger(3, 3, 1, 15, 0)
        mywin.flip()
        core.wait(0.5)

        fixation.draw()
        send_trigger(4, 15, 0, 4, 1)
        mywin.flip()
        core.wait(0.5)

    ###now present the fixation cue###
    fixation_cue.draw()
    send_trigger(5, 5, 1, 15, 0)
    mywin.flip()
    core.wait(2)

    ###present our cue number, followed by fixation###
    cues[cueOrder].draw()
    send_trigger(6, 15, 0, 6, 1)
    mywin.flip()
    core.wait(1)
    
    fixation.draw()
    send_trigger(7, 7, 1, 15, 0)
    mywin.flip()
    core.wait(0.3)

    ###determine which face we will present for the probe###
    if probeType >= 0:
        probeFace = learnFaces[probeType]
        print(probeFace)
    else:
        gotFaces = 0
        while gotFaces == 0:
            probeOptions = faceChoices[faceNum:]
            print(probeOptions)
            if matchGender:
                cueFace = learnFaces[cueOrder]
                if cueFace in womenIDs:
                    probeOptionsWomen = list(set(probeOptions).intersection(womenIDs))
                    probeOptions = probeOptionsWomen
                elif cueFace in menIDs:
                    probeOptionsMen = list(set(probeOptions).intersection(menIDs))
                    probeOptions = probeOptionsMen
                if not probeOptions:
                    shuffle(faceChoices)
                    learnFaces = faceChoices[0:faceNum]
                else:
                    probeFace = probeOptions[0]
                    print(probeFace)
                    gotFaces = 1

    ###now present our probe face and wait for a response###
    unfilt_faces[probeFace].draw()
    send_trigger(8, 15, 0, 8, 1)
    mywin.flip()
    core.wait(0.2)
    keys = event.waitKeys()
    while keys not in response_keys:
        keys = event.waitKeys()

    if keys == response_keys[0]: ###responsed YES###
        if probeType >= 0: ###face was presented in stream###
            if cueOrder == probeType: ###probe and cue are the same###
                trigger = 15
            else: ###probe and cue are different###
                trigger = 14
        else: ###face was not presented in the stream###
                trigger = 13
    elif keys == response_keys[1]:###responded NO###
        if probeType >= 0: ###face was presented in stream###
            if cueOrder == probeType: ###probe and cue are the same###
                trigger = 10
            else: ###probe and cue are different###
                trigger = 11
        else: ###face was not presented in the stream###
                trigger = 12
            
    send_trigger(trigger, trigger, 1, 15, 0)

    ###wait for a bit after a response###
    core.wait(0.5)
    send_trigger(0, 15, 0, 15, 0)

    correctResponse = trials_CueProbeAnswer[i_trial][2]          
    trial_usedFaceIDs.append(str(np.asarray(usedFaceIDs)))
    trial_faceChoices.append(str(np.asarray(faceChoices)))
    trial_learnFaces.append(str(np.asarray(learnFaces)))
    trial_cueOrder.append(cueOrder)
    trial_probeFace.append(probeFace)
    trial_probeType.append(probeType)
    trial_correctResponse.append(correctResponse)
    trial_resp.append(trigger)

    usedFaceIDs = learnFaces + [probeFace]

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

np.savetxt(filename_part, (trial_usedFaceIDs, trial_faceChoices, trial_learnFaces, trial_cueOrder, trial_probeFace, trial_probeType, trial_correctResponse, trial_resp), delimiter=',',fmt="%s")

core.wait(0.5)
done1.draw()
done2.draw()
mywin.flip()
event.waitKeys()
core.wait(1)

# Cleanup   
core.wait(0.5)
GPIO.cleanup()
mywin.close()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:  
    core.wait(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    core.wait(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")

