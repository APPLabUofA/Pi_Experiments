# -*- coding: utf-8 -*-

"""
Attentional Blink experiment

Find the two numbers in the stream.

Enter "999" to quit experiment.

"""

from expyriment import *
import random
import RPi.GPIO as GPIO
from pylsl import StreamInfo, StreamOutlet, local_clock
import numpy
import os
import sys
import time

partnum = sys.argv[1]
device = sys.argv[2]
filename = sys.argv[3]
exp_loc = sys.argv[4]

##control.set_develop_mode(True) # <--  comment
########### DESIGN ####################

###setup pins for triggers###
GPIO.setmode(GPIO.BCM)
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

###Setup our function to send triggers###
###trig_type is either 's' or 'r'###
###trig_num must be between 1-15###
def pi2trig(trig_type,trig_num):
    
    if trig_type == 's':
        pi_pins = [4,17,27,22]
    elif trig_type == 'r':       
        pi_pins = [5,6,13,19]
    elif trig_type == 'sr':
        pi_pins = [4,17,27,22,5,6,13,19]
    
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

##Colour schemes:
bg_colour = misc.constants.C_GREY
#bg_colour = misc.constants.C_BLACK

exp = design.Experiment("Blinking_Magnitude", background_colour=bg_colour,
                        foreground_colour = misc.constants.C_BLACK)

#Variables:
numbers = [1,2,3,4,6,7,8,9]
lags = (3,3,7,7)
trial_count = (len(numbers)*len(lags)*(len(numbers)-1))
letters = [letter for letter in 'ABCDEFGHJKLMNPQRSTUVWXYZ']
ISI = 90 #Inter-Stimulus-Interval: 100 ms
items = 16 #Number of letters per trial (+ 2 Numbers)
textsize = 44 #Stimuli size
trial_let = []
trial_t1_num = []
trial_t2_num = []
trial_lag = []
trial_resp = []
trial_t1_lag = []
trial_t2_lag = []
trig_t1_times = []
trig_t2_times = []


for bl_name in ["Block1"]:
    block = design.Block(name=bl_name)
    for lag in (3,3,7,7):#range(1,8+1):
        for t1 in numbers:
            for t2 in numbers:
                if t1 != t2:
                    tr = design.Trial()
                    tr.set_factor("lag", lag)
                    tr.set_factor("T1", t1)
                    tr.set_factor("T2", t2)
                    t1pos = design.randomize.rand_int(3,7)
                    tr.set_factor("T1_pos", t1pos)
                    #make rsvp stimulus stream
                    random.shuffle(letters)
                    stream = letters[0:items]
                    stream.insert(t1pos-1, t1)
                    stream.insert(t1pos-1+lag, t2)
                    for stim in stream:
                            tr.add_stimulus(stimuli.TextLine(text=str(stim),
                                            text_colour = misc.constants.C_BLACK,
                                            text_size=textsize))

                    block.add_trial(tr)
    block.shuffle_trials()
    exp.add_block(block)


exp.data_variable_names = ["trial_cnt", "T1_Position", "Time_lag",
                           "T1", "T2", "Difference",
                           "T1_Resp", "T2_Resp",
                           "RT", "Correct", "Reversed"]

######### INITIALIZE ##############
control.initialize(exp)

blank = stimuli.BlankScreen()
blank.preload()
fixcross = stimuli.FixCross()
fixcross.preload()

number_input = io.TextInput(message="Answer:",
                    message_text_size = 24,
                    user_text_size = 24,
                    ascii_filter=range(ord("1"), ord("9")+1))
#Trial:
def run_trial(trial, trial_cnt):
    blank.present()
    exp.clock.wait(1000 - trial.preload_stimuli())

    GPIO.output(pi2trig('s',15),0)
    GPIO.output(pi2trig('r',15),0)

    fixcross.present()
    exp.clock.wait(1000) #1 second Fixation Cross

    # present stream
    temp = []
    temp_let = str()
    count = 0
    for stim in trial.stimuli:
        if trial_cnt > -1:
            temp_let = temp_let + str(stim.text)
            if stim.text in str(numbers):
                count = count + 1
                if count == 1:
                    trig_t1_times.append(time.time() - start_exp)
                elif count == 2:
                    trig_t2_times.append(time.time() - start_exp)
                temp.append(str(stim.text))
                timestamp = local_clock()
                outlet.push_sample([int(block._trials[trial_cnt]._factors['lag'])], timestamp)
                GPIO.output(pi2trig('s',int(stim.text)),1)
                GPIO.output(pi2trig('r',int(block._trials[trial_cnt]._factors['lag'])),1)
            elif stim.text not in str(numbers):
                timestamp = local_clock()
                outlet.push_sample([10], timestamp)
                GPIO.output(pi2trig('s',10),1)
                GPIO.output(pi2trig('r',10),1)
        stim.present()
        exp.clock.wait(ISI/3)
        GPIO.output(pi2trig('s',15),0)
        GPIO.output(pi2trig('r',15),0)
        exp.clock.wait((ISI/3)*2)

    blank.present()
    if trial_cnt > -1:
        trial.unload_stimuli()
        trial_let.append(temp_let)
        trial_t1_num.append(int(temp[0]))
        trial_t2_num.append(int(temp[1]))
        trial_lag.append(int(block._trials[trial_cnt]._factors['lag']))
        trial_t1_lag.append(int(block._trials[trial_cnt]._factors['T1_pos']))
        trial_t2_lag.append(int(block._trials[trial_cnt]._factors['T1_pos'])+int(block._trials[trial_cnt]._factors['lag']))

    exp.clock.reset_stopwatch()
    input_ok = False
  
    while(not input_ok):
        exp.keyboard.clear()
        answer = number_input.get()
        if answer == "999":
            control.end()
            quit()
        if len(answer) == 2:
            input_ok = True
        else:
            stimuli.TextLine("Enter the two numbers:", text_size=24).present()
            exp.clock.wait(3000)

    RT = exp.clock.stopwatch_time

    n1 = answer[0]
    n2 = answer[1]
  
    t1 = trial.get_factor("T1")
    t2 = trial.get_factor("T2")

    correct = (t1, t2) == (int(n1), int(n2)) #did the subject enter the correct numbers?
    reverse = False
    if not correct:
        reverse = (t1, t2) == (int(n2), int(n1)) #correct numbers but wrong order?
    if trial_cnt > -1:
        if correct and not reverse:
                timestamp = local_clock()
                outlet.push_sample([15], timestamp)
                GPIO.output(pi2trig('s',15),1)
                GPIO.output(pi2trig('r',15),1)
                trial_resp.append('11')
        elif not correct and reverse:
                timestamp = local_clock()
                outlet.push_sample([14], timestamp)
                GPIO.output(pi2trig('s',14),1)
                GPIO.output(pi2trig('r',14),1)
                trial_resp.append('22')
        elif not correct and not reverse:
            if t1 == int(n1):
                timestamp = local_clock()
                outlet.push_sample([13], timestamp)
                GPIO.output(pi2trig('s',13),1)
                trial_resp.append('10')
            elif t2 == int(n2):
                timestamp = local_clock()
                outlet.push_sample([13], timestamp)
                GPIO.output(pi2trig('r',13),1)
                trial_resp.append('01')
            else:
                timestamp = local_clock()
                outlet.push_sample([12], timestamp)
                GPIO.output(pi2trig('s',12),1)
                timestamp = local_clock()
                trial_resp.append('00')

    semantic_diff = t2-t1 #semantic difference between the presented numbers

    exp.data.add([ trial_cnt, trial.get_factor("T1_pos"),
                   trial.get_factor("lag"),
                   t1, t2, abs(semantic_diff),
                   str(n1), str(n2), RT,
                   int(correct), int(reverse)])
    exp.data.save()



######### START ##############
control.start(exp)

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

#instruction:
stimuli.TextScreen("Find the two numbers!", "Enter '999' to quit experiment")
exp.keyboard.wait(misc.constants.K_SPACE)

start_exp = time.time()
timestamp = local_clock()
outlet.push_sample([11], timestamp)
GPIO.output(pi2trig('s',11),1)
GPIO.output(pi2trig('r',11),1)


# training
for x in range(10):
    trial = exp.blocks[0].get_random_trial()
    run_trial(trial, -1)

GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

stimuli.TextScreen(u"Questions?", "", heading_size=40).present()
exp.keyboard.wait(misc.constants.K_SPACE)

# Experiment

for block in exp.blocks:
    stimuli.TextScreen("Experiment starts now!", u"press space bar...").present()
    exp.keyboard.wait(misc.constants.K_SPACE)
    for cnt, trial in enumerate(block.trials):
        run_trial(trial, cnt)
        if cnt in [int(trial_count*0.2),int(trial_count*0.4),int(trial_count*0.6),int(trial_count*0.8)]:
            exp.clock.wait(100)
            GPIO.output(pi2trig('s',15),0)
            GPIO.output(pi2trig('r',15),0)
            exp.clock.wait(100)
            timestamp = local_clock()
            outlet.push_sample([11], timestamp)
            GPIO.output(pi2trig('s',11),1)
            stimuli.TextScreen("Pause!", u"press space bar...").present()
            exp.keyboard.wait(misc.constants.K_SPACE)
##        if cnt == 2:
##            break

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

numpy.savetxt(filename_part, (trial_let,trial_t1_num,trial_t2_num,trial_t1_lag,trial_t2_lag,trial_lag,trig_t1_times,trig_t2_times,trial_resp), delimiter=',',fmt="%s")
GPIO.cleanup()

####### END EXPERIMENT ########
control.end(goodbye_text="Thank you very much for participating in our experiment",
             goodbye_delay=2000)

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
