import os
import sys
from random import randint, shuffle
import numpy
from psychopy import visual, core, event
import RPi.GPIO as GPIO
from pylsl import StreamInfo, StreamOutlet, local_clock

partnum = sys.argv[1]
device = sys.argv[2]
filename = sys.argv[3]
exp_loc = sys.argv[4]

trials = 300 ###300 for experiment
###get GPIO pins ready###
GPIO.setmode(GPIO.BCM)

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

###initialise pygame###
mywin = visual.Window([592,448], monitor='testMonitor', units='deg', winType='pygame',
                      fullscr=False)

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

def wait_after_resp(start_time,wait_time):
    if core.getTime() - start_time < wait_time:
        core.wait(wait_time-(core.getTime() - start_time))

###setup the display screen and fixation###
mywin.mouseVisible = False
fixation = visual.GratingStim(win=mywin, size = 0.2, pos = [0,0], sf = 0, rgb = [1,1,1])
rect_size = 100
rect_green = (0,255,0)
rect_red = (255,0,0)

###define the number of trials, and tones per trial###
con_left_rate = 0.25
con_right_rate = 0.25
incon_left_rate = 0.25
incon_right_rate = 0.25
con_right_trial = (numpy.zeros(int(trials*con_left_rate)))+1
con_left_trial = (numpy.zeros(int(trials*con_right_rate)))+2
incon_left_trial = (numpy.zeros(int(trials*incon_left_rate)))+3
incon_right_trial = (numpy.zeros(int(trials*incon_right_rate)))+4
con_left_list = con_left_trial.tolist()
con_right_list = con_right_trial.tolist()
incon_left_list = incon_left_trial.tolist()
incon_right_list = incon_right_trial.tolist()
trial_order= con_left_list + incon_left_list + con_right_list + incon_right_list
practice_trial_order= con_left_list[0:int(len(trial_order)*0.025)] + incon_left_list[0:int(len(trial_order)*0.025)]  + con_right_list[0:int(len(trial_order)*0.025)]  + incon_right_list[0:int(len(trial_order)*0.025)] 
shuffle(trial_order)
shuffle(practice_trial_order)

exp_start = []
trial_response = []
trial_feedback = []
trial_quick = []
trial_type = []
trial_time = []
trial_delay = []

###set triggers to 0###
GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

###setup our instruction screens###
instr1 = visual.TextStim(win=mywin,text='Focus on the central fixation.',pos=(0,-1))
instr2 = visual.TextStim(win=mywin,text='Indicate which way the CENTRAL arrow is pointing.',pos=(0,-2))
instr3 = visual.TextStim(win=mywin,text='Please respond as quickly and as accurately as possible.',pos=(0,-3))
instr4 = visual.TextStim(win=mywin,text='Press the spacebar to begin practice trials.',pos=(0,-4))
instr5 = visual.TextStim(win=mywin,text='If you have any questions, please ask the experimenter.',pos=(0,-1))
instr6 = visual.TextStim(win=mywin,text='Press the spacebar when you are ready to begin.',pos=(0,-2))
break1 = visual.TextStim(win=mywin,text='Feel free to take a break at this time.',pos=(0,-1))
break2 = visual.TextStim(win=mywin,text='Please respond quickly and accurately.',pos=(0,-2))
break3 = visual.TextStim(win=mywin,text='Press the spacebar when you are ready to start.',pos=(0,-3))
end1 = visual.TextStim(win=mywin,text='Congratulations, you have finished the experiment!',pos=(0,-1))
end2 = visual.TextStim(win=mywin,text='Please contact the experimenter.',pos=(0,-2))

###define our trial conditions###
congruentright = visual.TextStim(win=mywin,text='>>>>>>>',pos=(0,0),height=1.25)
congruentleft = visual.TextStim(win=mywin,text='<<<<<<<',pos=(0,0),height=1.25)
incongruentright = visual.TextStim(win=mywin,text='<<<><<<',pos=(0,0),height=1.25)
incongruentleft = visual.TextStim(win=mywin,text='>>><>>>',pos=(0,0),height=1.25)

###define our feedback###
correct_resp = visual.Rect(win=mywin,width=1,height=1,pos=(0,0),lineColor=[0,1,0],fillColor=[0,1,0])
incorrect_resp = visual.Rect(win=mywin,width=1,height=1,pos=(0,0),lineColor=[1,0,0],fillColor=[1,0,0])

###show our instructions, and wait for a response###
fixation.draw()
instr1.draw()
instr2.draw()
instr3.draw()
instr4.draw()
mywin.flip()

###wait for button press to start experiment###
start_time = core.getTime()
keys = event.waitKeys()
while keys not in [['space']]:
    keys = event.waitKeys()

###first some practice trials###
for i_trial in range(len(practice_trial_order)):
    ITI = (randint(0,500)*0.001)+0.5
    fixation.draw()
    mywin.flip()
    core.wait(1)
    mywin.flip()
    core.wait(0.5)
    ###check to see which stimuli will be displayed for this trial###
    if practice_trial_order[i_trial] == 1:#congruent right
        trigger = 1
        congruentright.draw()
    elif practice_trial_order[i_trial] == 2:#congruent left
        trigger = 2
        congruentleft.draw()
    elif practice_trial_order[i_trial] == 3:#incongruent left
        trigger = 3
        incongruentleft.draw()
    elif practice_trial_order[i_trial] == 4:#incongruent right
        trigger = 4
        incongruentright.draw()
    ###briefly show stimuli and send trigger###
    mywin.flip()
    start_time = core.getTime()
    quick_response = []
    keys = event.waitKeys(0.2)
    if core.getTime() - start_time < 0.2:
        quick_response = keys
    wait_after_resp(start_time,0.2)
    mywin.flip()
    ###wait for response and send trigger when participant responds###
    start_time = core.getTime()
    keys = event.waitKeys(1.1)
    response = keys
    wait_after_resp(start_time,1.1)
    ###check to see if they responded before 200ms ended###
    if quick_response != []:
        response = quick_response
    ###present feedback###
    if response not in[['left'],['right']]:###did not respond
        incorrect_resp.draw()
        resp_trigger = 7
    elif response == ['right'] and trigger == 1:###responded right to congruent right###
        correct_resp.draw()
        resp_trigger = 15
    elif response == ['left'] and trigger == 1:###responded left to congruent right###
        incorrect_resp.draw()
        resp_trigger = 14
    elif response == ['right'] and trigger == 2:###responded right to congruent left###
        incorrect_resp.draw()
        resp_trigger = 13
    elif response == ['left'] and trigger == 2:###responded left to congruent left###
        correct_resp.draw()
        resp_trigger = 12
    elif response == ['right'] and trigger == 3:###responded right to incongruent left###
        incorrect_resp.draw()
        resp_trigger = 11
    elif response == ['left'] and trigger == 3:###responded left to incongruent left###
        correct_resp.draw()
        resp_trigger = 10
    elif response == ['right'] and trigger == 4:###responded right to incongruent right###
        correct_resp.draw()
        resp_trigger = 9
    elif response == ['left'] and trigger == 4:###responded left to incongruent right###
        incorrect_resp.draw()
        resp_trigger = 8
    ###send feedback, triggers and wait for a bit
    mywin.flip()
    core.wait(0.2)
    ###remove feedback and wait for a bit###
    mywin.flip()
    core.wait(ITI)
    ###set triggers back to zero###
    GPIO.output(pi2trig('s',15),0)
    GPIO.output(pi2trig('r',15),0)
    quick_response = []
    response = []
    delay = []

###present more instructions###
instr5.draw()
instr6.draw()
mywin.flip()
core.wait(1)
event.waitKeys()
core.wait(1)

exp_start = core.getTime()
timestamp = local_clock()
outlet.push_sample([100], timestamp)
GPIO.output(pi2trig('r',1),1)
core.wait(1)
GPIO.output(pi2trig('r',15),0)

###now the main experiment###
for i_trial in range(len(trial_order)):
    ITI = (randint(0,500)*0.001)+0.5
    trial_delay.append(ITI)
    ###check to see if there should be a break at the start of this trial###
    if (i_trial in (int(trials*0.10),int(trials*0.20),int(trials*0.30),int(trials*0.40),int(trials*0.50),int(trials*0.60),int(trials*0.70),int(trials*0.80),int(trials*0.90))):
        ###show the break screen, and wait for a response###
        break1.draw()
        break2.draw()
        break3.draw()
        timestamp = local_clock()
        outlet.push_sample([200], timestamp)
        GPIO.output(pi2trig('r',2),1)
        core.wait(1)
        GPIO.output(pi2trig('r',2),0)
        mywin.flip()
        keys = event.waitKeys()
        while keys not in [['space']]:
            keys = event.waitKeys()
        mywin.flip()
        core.wait(ITI)
        fixation.draw()
        timestamp = local_clock()
        outlet.push_sample([5], timestamp)
        GPIO.output(pi2trig('s',5),1)
        mywin.flip()
        core.wait(1)
        GPIO.output(pi2trig('s',15),0)
        mywin.flip()
        core.wait(0.5)
    else:###otherwise continue normally###
        fixation.draw()
        timestamp = local_clock()
        outlet.push_sample([5], timestamp)
        GPIO.output(pi2trig('s',5),1)
        mywin.flip()
        core.wait(1)
        GPIO.output(pi2trig('s',15),0)
        mywin.flip()
        core.wait(0.5)
    ###check to see which stimuli will be displayed for this trial###
    if trial_order[i_trial] == 1:#congruent right
        trigger = 1
        congruentright.draw()
    elif trial_order[i_trial] == 2:#congruent left
        trigger = 2
        congruentleft.draw()
    elif trial_order[i_trial] == 3:#incongruent left
        trigger = 3
        incongruentleft.draw()
    elif trial_order[i_trial] == 4:#incongruent right
        trigger = 4
        incongruentright.draw()
    ###briefly show stimuli and send trigger###
    trial_type.append(trigger)
    timestamp = local_clock()
    outlet.push_sample([trigger], timestamp)
    GPIO.output(pi2trig('s',trigger),1)
    trial_time.append(core.getTime()- exp_start)
    mywin.flip()
    start_time = core.getTime()
    quick_response = []
    keys = event.waitKeys(0.2)
    if core.getTime() - start_time < 0.2:
        timestamp = local_clock()
        outlet.push_sample([6], timestamp)
        GPIO.output(pi2trig('s',6),1)
        quick_response = keys
    wait_after_resp(start_time,0.2)
    GPIO.output(pi2trig('s',15),0)
    mywin.flip()
    ###wait for response and send trigger when participant responds###
    start_time = core.getTime()
    keys = event.waitKeys(1.1)
    response = keys
    timestamp = local_clock()
    outlet.push_sample([6], timestamp)
    GPIO.output(pi2trig('s',6),1)
    wait_after_resp(start_time,1.1)
    core.wait(0.1)
    GPIO.output(pi2trig('s',15),0)
    core.wait(0.1)
    ###check to see if they responded before 200ms ended###
    if quick_response != []:
        response = quick_response
        trial_quick.append(1)
    else:
        trial_quick.append(0)
    trial_response.append(response)
    ###present feedback###
    if response not in[['left'],['right']]:###did not respond
        incorrect_resp.draw()
        resp_trigger = 7
    elif response == ['right'] and trigger == 1:###responded right to congruent right###
        correct_resp.draw()
        resp_trigger = 15
    elif response == ['left'] and trigger == 1:###responded left to congruent right###
        incorrect_resp.draw()
        resp_trigger = 14
    elif response == ['right'] and trigger == 2:###responded right to congruent left###
        incorrect_resp.draw()
        resp_trigger = 13
    elif response == ['left'] and trigger == 2:###responded left to congruent left###
        correct_resp.draw()
        resp_trigger = 12
    elif response == ['right'] and trigger == 3:###responded right to incongruent left###
        incorrect_resp.draw()
        resp_trigger = 11
    elif response == ['left'] and trigger == 3:###responded left to incongruent left###
        correct_resp.draw()
        resp_trigger = 10
    elif response == ['right'] and trigger == 4:###responded right to incongruent right###
        correct_resp.draw()
        resp_trigger = 9
    elif response == ['left'] and trigger == 4:###responded left to incongruent right###
        incorrect_resp.draw()
        resp_trigger = 8
    ###send feedback, triggers and wait for a bit
    timestamp = local_clock()
    outlet.push_sample([resp_trigger], timestamp)
    GPIO.output(pi2trig('s',resp_trigger),1)
    mywin.flip()
    trial_feedback.append(resp_trigger)
    core.wait(0.1)
    GPIO.output(pi2trig('s',15),0)
    core.wait(0.1)
    ###remove feedback and wait for a bit###
    mywin.flip()
    core.wait(ITI)
    ###set triggers back to zero###
    GPIO.output(pi2trig('s',15),0)
    GPIO.output(pi2trig('r',15),0)
    quick_response = []
    response = []
    delay = []

###show the end screen###
end1.draw()
end2.draw()
fixation.draw()
timestamp = local_clock()
outlet.push_sample([300], timestamp)
GPIO.output(pi2trig('r',3),1)
mywin.flip()
event.waitKeys()
mywin.mouseVisible = True
GPIO.output(pi2trig('r',15),0)

###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

numpy.savetxt(filename_part, (trial_response,trial_type,trial_feedback,trial_quick,trial_time,trial_delay), delimiter=',',fmt="%s")

mywin.close()
GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:
    core.wait(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    core.wait(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
      
core.wait(1)
