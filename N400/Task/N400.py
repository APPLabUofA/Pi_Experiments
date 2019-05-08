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

stim_time = 0.6
ISI = 0.5
directions = ['LEFT','RIGHT']
shuffle(directions)

###get GPIO pins ready###
GPIO.setmode(GPIO.BCM)

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

###initialise pygame###
mywin = visual.Window([592,448], monitor='testMonitor', units='deg', winType='pygame',
                      fullscr=False)
mywin.mouseVisible = False

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
rect_size = 100
rect_green = (0,255,0)
rect_red = (255,0,0)
fixation = visual.GratingStim(win=mywin, size = 0.2, pos = [0,0], sf = 0, rgb = [1,1,1])

###define our word lists###

###########################
###first our related semantic words###
primes_semantic_related = [line.rstrip('\r\n') for line in open('/home/pi/research_experiments/Experiments/Stimuli/Word_Lists/related_prime.txt')]
targets_semantic_related = [line.rstrip('\r\n') for line in open('/home/pi/research_experiments/Experiments/Stimuli/Word_Lists/related_target.txt')]

###now combine lists and add an identifier###
order = numpy.zeros(len(primes_semantic_related))+1
semantic_related_list = zip(primes_semantic_related,targets_semantic_related,order)

###now take the first 5 trials to act as a practice###
shuffle(semantic_related_list)
semantic_related_practice = semantic_related_list[0:5]
semantic_related_list = semantic_related_list[5:(len(semantic_related_list)/2)+5]
###########################

###########################
###then our unrelated semantic words###
primes_semantic_unrelated = [line.rstrip('\r\n') for line in open('/home/pi/research_experiments/Experiments/Stimuli/Word_Lists/unrelated_prime.txt')]
targets_semantic_unrelated = [line.rstrip('\r\n') for line in open('/home/pi/research_experiments/Experiments/Stimuli/Word_Lists/unrelated_target.txt')]

###now combine lists and add an identifier###
order = numpy.zeros(len(primes_semantic_unrelated))+2
semantic_unrelated_list = zip(primes_semantic_unrelated,targets_semantic_unrelated,order)

###now take the first 5 trials to act as a practice###
shuffle(semantic_unrelated_list)
semantic_unrelated_practice = semantic_unrelated_list[0:5]
semantic_unrelated_list = semantic_unrelated_list[5:(len(semantic_unrelated_list)/2)+5]
###########################

###########################
###now combine our lists###
semantic_combined_list = semantic_related_list + semantic_unrelated_list
shuffle(semantic_combined_list)
semantic_combined_practice = semantic_related_practice + semantic_unrelated_practice
shuffle(semantic_combined_practice)
###########################

###########################
###now for our related normative words###
primes_normative_related = [line.rstrip('\r\n') for line in open('/home/pi/research_experiments/Experiments/Stimuli/Word_Lists/related_prime_norm.txt')]
targets_normative_related = [line.rstrip('\r\n') for line in open('/home/pi/research_experiments/Experiments/Stimuli/Word_Lists/related_target_norm.txt')]

###now combine lists and add an identifier###
order = numpy.zeros(len(primes_normative_related))+3
normative_related_list = zip(primes_normative_related,targets_normative_related,order)

###now take the first 5 trials to act as a practice###
shuffle(normative_related_list)
normative_related_practice = normative_related_list[0:5]
normative_related_list = normative_related_list[5:(len(normative_related_list)/2)+5]
###########################

###########################
###then our unrelated normative words###
primes_normative_unrelated = [line.rstrip('\r\n') for line in open('/home/pi/research_experiments/Experiments/Stimuli/Word_Lists/unrelated_prime_norm.txt')]
targets_normative_unrelated = [line.rstrip('\r\n') for line in open('/home/pi/research_experiments/Experiments/Stimuli/Word_Lists/unrelated_target_norm.txt')]

###now combine lists and add an identifier###
order = numpy.zeros(len(primes_normative_unrelated))+4
normative_unrelated_list = zip(primes_normative_unrelated,targets_normative_unrelated,order)

###now take the first 5 trials to act as a practice###
shuffle(normative_unrelated_list)
normative_unrelated_practice = normative_unrelated_list[0:5]
normative_unrelated_list = normative_unrelated_list[5:(len(normative_unrelated_list)/2)+5]
###########################

###########################
###now combine our lists###
normative_combined_list = normative_related_list + normative_unrelated_list
shuffle(normative_combined_list)
normative_combined_practice = normative_related_practice + normative_unrelated_practice
shuffle(normative_combined_practice)
###########################

###########################
###now we will combine our semantic and normative lists###
trial_order = semantic_combined_list + normative_combined_list
shuffle(trial_order)
trial_order_practice = semantic_combined_practice + normative_combined_practice
shuffle(trial_order_practice)

###here we will preload each of our stimuli so they are ready to present###
trial_order_practice_1 = numpy.zeros(len(trial_order_practice))
trial_order_practice_2 = numpy.zeros(len(trial_order_practice))
trial_order_practice_3 = numpy.zeros(len(trial_order_practice))
trial_order_practice_1 = trial_order_practice_1.tolist()
trial_order_practice_2 = trial_order_practice_2.tolist()
trial_order_practice_3 = trial_order_practice_3.tolist()
for i_word in range(len(trial_order_practice)):
    trial_order_practice_1[i_word] = visual.TextStim(win=mywin,text=trial_order_practice[i_word][0],pos=(0,0))
    trial_order_practice_2[i_word] = visual.TextStim(win=mywin,text=trial_order_practice[i_word][1],pos=(0,0))
    trial_order_practice_3[i_word] = trial_order_practice[i_word][2]

trial_order_practice = zip(trial_order_practice_1,trial_order_practice_2,trial_order_practice_3)

trial_order_1 = numpy.zeros(len(trial_order))
trial_order_2 = numpy.zeros(len(trial_order))
trial_order_3 = numpy.zeros(len(trial_order))
trial_order_1 = trial_order_1.tolist()
trial_order_2 = trial_order_2.tolist()
trial_order_3 = trial_order_3.tolist()
for i_word in range(len(trial_order)):
    trial_order_1[i_word] = visual.TextStim(win=mywin,text=trial_order[i_word][0],pos=(0,0))
    trial_order_2[i_word] = visual.TextStim(win=mywin,text=trial_order[i_word][1],pos=(0,0))
    trial_order_3[i_word] = trial_order[i_word][2]

trial_order = zip(trial_order_1,trial_order_2,trial_order_3)

###setup some variables to keep track of things###
exp_start = []
trial_response = []
trial_type = []
trial_time = []
trial_delay = []
trial_direction = []

###set triggers to 0###
GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

###setup our instruction screens###
instr1 = visual.TextStim(win=mywin,text='Focus on the central fixation.',pos=(0,-1))
instr2 = visual.TextStim(win=mywin,text='You will see two words, presented one after the other.',pos=(0,-2))
instr3 = visual.TextStim(win=mywin,text='For RELATED words, press ' + directions[0] +'.',pos=(0,-3))
instr4 = visual.TextStim(win=mywin,text='For UNRELATED words, press ' + directions[1] +'.',pos=(0,-4))
instr5 = visual.TextStim(win=mywin,text='Press the spacebar for several practice trials.',pos=(0,-5))
instr6 = visual.TextStim(win=mywin,text='Contact the experimenter if you have any questions.',pos=(0,-1))
instr7 = visual.TextStim(win=mywin,text='To begin the main experiment, press the spacebar.',pos=(0,-2))
break1 = visual.TextStim(win=mywin,text='Feel free to take a break at this time.',pos=(0,-1))
break2 = visual.TextStim(win=mywin,text='Press the spacebar when you are ready to start.',pos=(0,-2))
resp1 = visual.TextStim(win=mywin,text='RELATED (' + directions[0] +')',pos=(0,-1))
resp2 = visual.TextStim(win=mywin,text='UNRELATED (' + directions[1] +')',pos=(0,-2))
end1 = visual.TextStim(win=mywin,text='Congratulations, you have finished the experiment!',pos=(0,-1))
end2 = visual.TextStim(win=mywin,text='Please contact the experimenter.',pos=(0,-2))

###show our instructions, and wait for a response###
fixation.draw()
instr1.draw()
instr2.draw()
instr3.draw()
instr4.draw()
instr5.draw()
mywin.flip()

###wait for button press to start experiment###
start_time = core.getTime()
keys = event.waitKeys()
while keys not in [['space']]:
    keys = event.waitKeys()

###first we will run the practice trials###
for i_trial in range(len(trial_order_practice)):
    ITI = (randint(0,500)*0.001)+0.5
    ###wait a bit###
    mywin.flip()
    core.wait(ITI)
    ###present fixation cross###
    fixation.draw()
    mywin.flip()
    core.wait(1)
    ###now remove the fixation and wait for a bit###
    mywin.flip()
    core.wait(0.5)
    ###present our prime word###
    trial_order_practice[i_trial][0].draw()
    mywin.flip()
    core.wait(stim_time)
    ###present a brief blank###
    mywin.flip()
    core.wait(ISI)
    ###now present our target word###
    trial_order_practice[i_trial][1].draw()
    mywin.flip()
    core.wait(stim_time)
    ###present a brief blank###
    mywin.flip()
    core.wait(ISI)
    ###now we wait for a response
    resp1.draw()
    resp2.draw()
    mywin.flip()
    start_time = core.getTime()
    keys = event.waitKeys(2)
    wait_after_resp(start_time,2)

###see if the participant has any questions###
instr6.draw()
instr7.draw()
mywin.flip()
core.wait(3)
start_time = core.getTime()
keys = event.waitKeys()
while keys not in [['space']]:
    keys = event.waitKeys()

###now begin the main experiment###
exp_start = core.getTime()
timestamp = local_clock()
outlet.push_sample([100], timestamp)
GPIO.output(pi2trig('r',1),1)
core.wait(1)
GPIO.output(pi2trig('r',1),0)
for i_trial in range(len(trial_order)):
    ITI = (randint(0,500)*0.001)+0.5
    trial_delay.append(ITI)
    ###check to see if there should be a break at the start of this trial###
    if (i_trial in (int(len(trial_order)*0.10),int(len(trial_order)*0.20),int(len(trial_order)*0.30),int(len(trial_order)*0.40),int(len(trial_order)*0.50),int(len(trial_order)*0.60),int(len(trial_order)*0.70),int(len(trial_order)*0.80),int(len(trial_order)*0.90))):
        ###show the break screen, and wait for a response###
        break1.draw()
        break2.draw()
        timestamp = local_clock()
        outlet.push_sample([200], timestamp)
        GPIO.output(pi2trig('r',2),1)
        core.wait(1)
        GPIO.output(pi2trig('r',2),0)
        mywin.flip()
        start_time = core.getTime()
        keys = event.waitKeys()
        while keys not in [['space']]:
            keys = event.waitKeys()
    ###otherwise continue normally###
    ###wait a bit###
    mywin.flip()
    core.wait(ITI)
    ###present fixation cross###
    fixation.draw()
    timestamp = local_clock()
    outlet.push_sample([10], timestamp)
    GPIO.output(pi2trig('s',10),1)
    mywin.flip()
    core.wait(1)
    GPIO.output(pi2trig('s',15),0)
    ###now remove the fixation and wait for a bit###
    mywin.flip()
    core.wait(0.5)
    ###present our prime word###
    trigger = int(trial_order[i_trial][2])
    trial_order[i_trial][0].draw()
    timestamp = local_clock()
    outlet.push_sample([trigger], timestamp)
    GPIO.output(pi2trig('s',trigger),1)
    mywin.flip()
    core.wait(stim_time)
    GPIO.output(pi2trig('s',15),0)
    ###present a brief blank###
    mywin.flip()
    core.wait(ISI)
    ###now present our target word###
    trigger = int(trial_order[i_trial][2]+4)
    trial_time.append(core.getTime() - exp_start)
    trial_type.append(trigger)
    trial_order[i_trial][1].draw()
    timestamp = local_clock()
    outlet.push_sample([trigger], timestamp)
    GPIO.output(pi2trig('s',trigger),1)
    mywin.flip()
    core.wait(stim_time)
    GPIO.output(pi2trig('s',15),0)
    ###present a brief blank###
    mywin.flip()
    core.wait(ISI)
    ###now we wait for a response
    resp1.draw()
    resp2.draw()
    mywin.flip()
    start_time = core.getTime()
    keys = event.waitKeys(2)
    response = keys
    if response == ['left']:###related###
        resp_trigger = 11
    elif response == ['right']:###unrelated###
        resp_trigger = 12
    elif response not in [['left'],['right']]:###no response###
        resp_trigger = 13
    trial_response.append(resp_trigger)
    timestamp = local_clock()
    outlet.push_sample([resp_trigger], timestamp)
    GPIO.output(pi2trig('s',resp_trigger),1)
    wait_after_resp(start_time,2)
    GPIO.output(pi2trig('s',15),0)
    trial_direction.append(directions[0])

###show the end screen###
end1.draw()
end2.draw()
fixation.draw()
timestamp = local_clock()
outlet.push_sample([300], timestamp)
GPIO.output(pi2trig('r',3),1)
mywin.flip()
start_time = core.getTime()
keys = event.waitKeys()
while keys not in [['space']]:
    keys = event.waitKeys()
mywin.mouseVisible = True
GPIO.output(pi2trig('r',15),0)
###save times###
filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

numpy.savetxt(filename_part, (trial_response,trial_type,trial_time,trial_delay,trial_direction), delimiter=',',fmt="%s")

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:  
    core.wait(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    core.wait(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
      
core.wait(1)
mywin.close()
GPIO.cleanup()
