##import all the needed packages##
import board
import neopixel
import RPi.GPIO as GPIO
import time
from random import randint, shuffle
import numpy as np
import os
from pylsl import StreamInfo, StreamOutlet, local_clock

###create our stream variables###
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')

###next make an outlet to record the streamed data###
outlet = StreamOutlet(info)

##setup some constant variables##
partnum = "001"
filename = 'visual_p3_gopro_visor'

##number of trials##
trial_num = 10

##number of blocks
block_num = 1

##standard and target rate##
standard_rate = 0.8
target_rate = 0.2

##several colours for the pixels##
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
blank = (0, 0, 0)
brightness = 0.2

##number of pixels we will be controlling##
pin_num = 6

##specify which pin we will be controlling the LEDs with##
pin_out = board.D18

##pins we will be using##
muse_pin = 5
resp_pin = 21

##amount of time needed to reset triggers##
trig_gap = 0.005

###initialise GPIO pins###
GPIO.setmode(GPIO.BCM)
GPIO.setup(muse_pin,GPIO.OUT)

###set triggers to 0###
GPIO.output(muse_pin,0)

###setup pin for push button###
GPIO.setup(resp_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def resp_trig(trig): # maps response trigger to standard (3) or target (4)
    if trig == 1:
        resp_trig = 3
    else:
        resp_trig = 4

def get_resp_led_off(pin, led_on_time,trig): # get response (if occured in first 1 second) + turn off the LEDs regardless
    start_resp = time.time()

    GPIO.wait_for_edge(pin,GPIO.RISING, timeout = int(led_on_time * 1000))

    button_down = time.time() - start_resp # this is response time from the start of the 1 second response window

    if button_down < led_on_time: ## right now this isn't making any sense to me
        resp_trig(trig)
        resp_time = button_down
        if button_down <= 0.990:
            time.sleep(led_on_time - (button_down + trig_gap*2)) # wait until the end of the 1 second of the light being on
    else:
        resp_time = 0

    # before_second_light = time.time() - start_exp
    pixels.fill(blank)
    # after_second_light = time.time() - start_resp
    if trig == 1: ## Maps out offset trigger to standard and target flashes
        timestamp = local_clock()
        outlet.push_sample([5], timestamp)
    else:
        timestamp = local_clock()
        outlet.push_sample([6], timestamp)

    return resp_time # before_second_light, after_second_light

def get_resp(pin, wait_time, prev_delay, resp, trig): # get response (if not in the first second) + wait for wait time (delay)
    start_resp = time.time()

    GPIO.wait_for_edge(pin,GPIO.RISING, timeout = int(wait_time * 1000))

    delay_end_time = time.time() - start_resp

    if resp == 0:
        resp_time = delay_end_time + prev_delay
        if resp_time <= 2.0:
            resp_trig(trig)
    else:
        resp_time = resp

    if delay_end_time < wait_time:
        time.sleep(wait_time - delay_end_time)

    return resp_time

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    return (r, g, b)


def rainbow_cycle(wait, rainbow_time):
    start = time.time()
    while time.time() - start < rainbow_time:
        for j in range(255):
            for i in range(pin_num):
                pixel_index = (i * 256 // pin_num) + j
                pixels[i] = wheel(pixel_index & 255)
            pixels.show()
            time.sleep(wait)

def refresh_fixation(): 
    img[int(width-width/100):int(width+width/100), int(height-height/20):int(height+height/20), :] = 255
    img[int(width-width/20):int(width+width/20), int(height-height/100):int(height+height/100), :] = 255

##distribution of targets and standards##
trials = np.zeros(int(trial_num*standard_rate)).tolist() + np.ones(int(trial_num*target_rate)).tolist()
shuffle(trials) # randomize order of standards and targets

##variables to save trial information##
trig_time   = []
trig_type = []
delay_length  = []
trial_resp = []
jitter_length = []
resp_latency = []
block_start_stop = []
exp_start_stop = []
trial_count = 0

##setup our neopixels##
pixels = neopixel.NeoPixel(pin_out, pin_num, brightness = brightness, auto_write = True)

##to significy the start of the experiment we make the LEDs all red initially and then wait for a certain amount of time##
for block in range(block_num):
    pixels.fill(red)
    GPIO.wait_for_edge(resp_pin,GPIO.RISING) ## Waits for an initial button press to turn on the LED (red)
    timestamp = local_clock()
    outlet.push_sample([3], timestamp)
    GPIO.output(muse_pin,1) # send unique trigger for the start of the block
    if block == 0:
        start_exp = time.time()
        exp_start_stop.append(0)
    trig_time.append(time.time() - start_exp)
    block_start_stop.append(time.time() - start_exp) # start of each block from start_exp
    ## structure output of CSV
    trig_type.append(3)
    delay_length.append(2)
    trial_resp.append(0)
    jitter_length.append(0)
    resp_latency.append(0)
    time.sleep(2) ## leave red on for 2 seconds
    pixels.fill(blank)
    GPIO.output(muse_pin,0)
    time.sleep(2)
    for i_trial in range(len(trials)):
        start_trial = time.time() + trig_gap # define start time of a given trial
        delay = ((randint(0,500)*0.001)+1.0) # define delay, to be used later
        delay_length.append(delay)
        ##determine the type of stimuli we will show on this trial##
        if trials[i_trial] == 0: #standards
            trig = 1
            pixels.fill(green)
        elif trials[i_trial] == 1: #targets
            trig = 2
            pixels.fill(blue)
        timestamp = local_clock()
        outlet.push_sample([3], timestamp)
        GPIO.output(muse_pin,1)
        trig_type.append(trig)
        trig_time.append(time.time() - start_exp)
        time.sleep(trig_gap)

        resp_time = get_resp_led_off(resp_pin, 1.0,trig)
        resp_time = get_resp(resp_pin, delay, 1.0, resp_time,trig)
        resp_latency.append(time.time() - start_exp)
        trial_resp.append(resp_time)

        GPIO.output(muse_pin,0)
        time.sleep(trig_gap)
        end_trial = time.time()

        actual_trial_length = end_trial - start_trial
        theoretical_trial_length = delay + 1.0
        jitter = actual_trial_length - theoretical_trial_length
        jitter_length.append(jitter)

        trial_count += 1
    ##end of block##
    pixels.fill(red)
    trig_time.append(time.time() - start_exp)
    block_start_stop.append(time.time() - start_exp) # end of each block from start_exp
    ## structure output of CSV
    trig_type.append(4)
    delay_length.append(2)
    trial_resp.append(0)
    jitter_length.append(0)
    resp_latency.append(0)
    time.sleep(2) ## leave red on for 2 seconds
    pixels.fill(blank)
    time.sleep(2)

# End of the experiment           
exp_start_stop.append(time.time() - start_exp)

rainbow_cycle(0.001, 5) ## After all blocks flash a rainbow at a refresh of (1st arguement) ms for (2nd arguement) seconds

pixels.fill(blank)

###save trial information###
while os.path.isfile("/home/pi/research_experiments/Experiments/Visual_P3_LED/Data/Muse/LSL_Trial_Information/" + partnum + "_" + filename + ".csv") == True:
    if int(partnum) >=10:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

filename_part = ("/home/pi/research_experiments/Experiments/Visual_P3_LED/Data/Muse/LSL_Trial_Information/" + partnum + "_" + filename + ".csv")

# What is each thing
# trig_type
# trig_time
# delay_length
# trial_resp
# jitter_length
# resp_latency
# start_stop

np.savetxt(filename_part, (trig_type,trig_time, delay_length, trial_resp, jitter_length, resp_latency, block_start_stop, exp_start_stop), delimiter=',',fmt="%s")

GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:  
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
