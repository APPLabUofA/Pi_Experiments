##import all the needed packages##
import board
import neopixel
#import pigpio
import RPi.GPIO as GPIO
import time
from random import randint, shuffle
import numpy as np
import cv2

#Define Window
screen_res = 1080,1920 
width = int(screen_res[0]/2) # half width
height = int(screen_res[1]/2) # half height

#Define Instructions
instr_0 = 'Press the space bar once to continue'
instr_1 = 'During the duration of the experiment, focus on central fixation'
instr_2 = 'Press the button when you see blue flashes'
instr_3 = 'Do NOT press the button when you see green flashes.'
instr_4 = 'When you are ready to start, press the space bar and THEN the button.'
instr_5 = 'Feel free to take a break at this time.'
instr_6 = 'To continue the experiment, press the space bar and THEN the button.'
instr_7 = 'Congratulations, you have finished the experiment!'
instr_8 = 'Please contact the experimenter.'

# Instruct lists for looping 
Space_Propmt = [instr_0]
Start_Instruct = [instr_0,instr_1, instr_2, instr_3, instr_4]
Break_Instruct = [instr_5, instr_6]
End_Instruct = [instr_7, instr_8]

# Positions of text # Change all these - independent of aspect ratio
Space_Propmt_Width = [(int(screen_res[1]/3),int(screen_res[1]/3))]
Start_Instruct_Width = [(int(screen_res[1]/3),int(screen_res[1]/3)),(int(screen_res[1]/5),int(screen_res[1]/3)),(int(screen_res[1]/3),int(screen_res[1]/3)),(int(screen_res[1]/4),int(screen_res[1]/3)),(int(screen_res[1]/6),int(screen_res[1]/3)),(int(screen_res[1]/4),int(screen_res[1]/3))]
Break_Instruct_Width = [(int(screen_res[1]/3),int(screen_res[1]/3)),(int(screen_res[1]/6),int(screen_res[1]/2))]
End_Instruct_Width =  [(int(screen_res[1]/4),int(screen_res[1]/3)),(int(screen_res[1]/3),int(screen_res[1]/2))]

##setup some constant variables##
partnum = input("partnum: ")
filename = 'visual_p3_gopro_visor'

##number of trials##
trial_num = int(input("How many trials per block?: "))

##number of blocks
block_num = int(input("How many blocks?: "))

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
trig_pins = [4,17,27,22,5,6,13,19]
resp_pin = 21

##amount of time needed to reset triggers##
trig_gap = 0.005

##define the ip address for the second Pi we will be controlling##
##pi = pigpio.pi('192.168.1.216')

###initialise GPIO pins###
GPIO.setmode(GPIO.BCM)
GPIO.setup(trig_pins,GPIO.OUT)

###set triggers to 0###
GPIO.output(trig_pins,0)

###setup pin for push button###
GPIO.setup(resp_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def pi2trig(trig_num):

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

def resp_trig(trig): # maps response trigger to standard (3) or target (4)
    if trig == 1:
        resp_trig = 3
    else:
        resp_trig = 4
    GPIO.output(pi2trig(resp_trig),1)
    time.sleep(trig_gap)
    GPIO.output(pi2trig(255),0)
    time.sleep(trig_gap)


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
        GPIO.output(pi2trig(5),1)
    else:
        GPIO.output(pi2trig(6),1)
    time.sleep(trig_gap)
    GPIO.output(pi2trig(255),0)

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

def refresh_trig_visor(x): # structure output of CSV
    trig_type.append(x)
    delay_length.append(2)
    trial_resp.append(0)
    resp_latency.append(0)
    time.sleep(2) ## leave red on for 2 seconds
    pixels.fill(blank)
    GPIO.output(pi2trig(255),0)
    
##define the ip address for the second Pi we will be controlling##
##pi = pigpio.pi('192.168.1.216')

##distribution of targets and standards##
trials = np.zeros(int(trial_num*standard_rate)).tolist() + np.ones(int(trial_num*target_rate)).tolist()
shuffle(trials) # randomize order of standards and targets

##variables to save trial information##
trig_time   = []
trig_type = []
delay_length  = []
trial_resp = []
resp_latency = []
block_start_stop = []
exp_start_stop = []
trial_count = 0

##setup our neopixels##
pixels = neopixel.NeoPixel(pin_out, pin_num, brightness = brightness, auto_write = True)

##to significy the start of the experiment we make the LEDs all red initially and then wait for a certain amount of time##

#Construct window + draw instructions before the experiment begins
if __name__ == '__main__':
    window_name = 'projector'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    for i in range(len(Start_Instruct)):
        img = np.zeros((int(screen_res[0]),int(screen_res[1]),3), np.uint8) # 1960 X 1200 X 3 # all zeros = all black
        cv2.putText(img,Start_Instruct[i],Start_Instruct_Width[i], cv2.FONT_HERSHEY_COMPLEX_SMALL , 1,(255,255,255),2,cv2.LINE_AA)
        refresh_fixation()
        cv2.imshow(window_name, img)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
######## Actual Experiment Starts  ######
    for block in range(block_num):
        img = np.zeros((int(screen_res[0]),int(screen_res[1]),3), np.uint8) # 1960 X 1200 X 3 # all zeros = all black
        refresh_fixation()
        cv2.imshow(window_name, img)
        cv2.waitKey(10)
        GPIO.wait_for_edge(resp_pin,GPIO.RISING) ## Waits for an initial button press to turn on the LED (red)
        pixels.fill(red)
        GPIO.output(pi2trig(10),1) # send unique trigger for the start of the block
        if block == 0:
            start_exp = time.time()
            exp_start_stop.append(0)
        trig_time.append(time.time() - start_exp)
        block_start_stop.append(time.time() - start_exp) # start of each block from start_exp
        refresh_trig_visor(3)
        time.sleep(2)
        for i_trial in range(len(trials)):
            start_trial = time.time() + trig_gap # define start time of a given trial
            delay = ((randint(0,500)*0.001)+1.0) # define delay, to be used later
            delay_length.append(delay)
            ##determine the type of stimuli we will show on this trial##
            if trials[i_trial] == 0: #standards
                trig = 1
                pixels.fill(green)
        ##                pi.write(4, 1)
            elif trials[i_trial] == 1: #targets
                trig = 2
                pixels.fill(blue)
        ##                pi.write(17, 1)
            GPIO.output(pi2trig(trig),1) ## Specify which trigger to send Standard vs Target
            trig_type.append(trig)
            trig_time.append(time.time() - start_exp)
            time.sleep(trig_gap)

            GPIO.output(pi2trig(255),0)
            resp_time = get_resp_led_off(resp_pin, 1.0,trig) # before_second_light, after_second_light
            resp_time = get_resp(resp_pin, delay, 1.0, resp_time,trig)
            resp_latency.append(time.time() - start_exp)
            trial_resp.append(resp_time)

            GPIO.output(pi2trig(255),0) ## doesn't give us a trigger
            time.sleep(trig_gap)
            end_trial = time.time()


            trial_count += 1
        ##end of block##
        pixels.fill(red)
        GPIO.output(pi2trig(11),1) # send unique trigger for the end of a block
        trig_time.append(time.time() - start_exp)
        block_start_stop.append(time.time() - start_exp) # end of each block from start_exp
        refresh_trig_visor(4)
        time.sleep(2)
        # Break Screen Instructions
        if trial_count < block_num:
            img = np.zeros((int(screen_res[0]),int(screen_res[1]),3), np.uint8) # 1960 X 1200 X 3 # all zeros = all black
            cv2.putText(img,Break_Instruct[0],Break_Instruct_Width[0], cv2.FONT_HERSHEY_COMPLEX_SMALL , 1,(255,255,255),2,cv2.LINE_AA)
            cv2.putText(img,Break_Instruct[1],Break_Instruct_Width[1], cv2.FONT_HERSHEY_COMPLEX_SMALL , 1,(255,255,255),2,cv2.LINE_AA)
            refresh_fixation()
            cv2.imshow(window_name, img)
            cv2.waitKey(0)

# End of the experiment           
exp_start_stop.append(time.time() - start_exp)
img = np.zeros((int(screen_res[0]),int(screen_res[1]),3), np.uint8) # 1960 X 1200 X 3 # all zeros = all black
cv2.putText(img,End_Instruct[0],End_Instruct_Width[0], cv2.FONT_HERSHEY_COMPLEX_SMALL , 1,(255,255,255),2,cv2.LINE_AA)
cv2.putText(img,End_Instruct[1],End_Instruct_Width[1], cv2.FONT_HERSHEY_COMPLEX_SMALL , 1,(255,255,255),2,cv2.LINE_AA)
cv2.imshow(window_name, img)
cv2.waitKey(0)

rainbow_cycle(0.001, 5) ## After all blocks flash a rainbow at a refresh of (1st arguement) ms for (2nd arguement) seconds

pixels.fill(blank)
cv2.destroyAllWindows()

###save trial information###
filename_part = ("/home/pi/GitHub/GoPro_Visor_Eye_Pi/Pilot_Data/Experiment_1/" + partnum + "_" + filename + ".csv")


np.savetxt(filename_part, (trig_type,trig_time, delay_length, trial_resp, resp_latency, block_start_stop, exp_start_stop), delimiter=',',fmt="%s")
