import time
import os
from random import randint, shuffle
##import blinkt
from psychopy import visual, core, event
import RPi.GPIO as GPIO
import numpy as np

###initialise pygame###
GPIO.setmode(GPIO.BCM)

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

###setup the display screen and fixation###
mywin = visual.Window([592,448], monitor='testMonitor', units='deg', winType='pygame',
                      fullscr=False,color='black')
mywin.mouseVisible = False

stim = visual.Rect(win=mywin, width=10,height=10,pos=(0,0),fillColor='white')
rect_size = 10000
rect_green = (0,255,0)

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

###set triggers to 0###
GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

###for this, we will present 10 stimuli for 1 second each using different methods###

##event.waitKeys()
draw_list = []
flip_list = []
wait_list = []

for i_blink in range(10000):
    GPIO.output(pi2trig('s',1),1)
    start_stim = core.getTime()
    stim.draw()
    draw_list.append(core.getTime() - start_stim)
    start_stim = core.getTime()
    mywin.flip()
    flip_list.append(core.getTime() - start_stim)
    start_stim = core.getTime()
    core.wait(0.2)
    wait_list.append((core.getTime() - start_stim)-0.2)
    mywin.flip()
    GPIO.output(pi2trig('s',15),0)
    core.wait(0.2)

print(np.mean(draw_list[1:]))
print(np.mean(flip_list))
print(np.mean(wait_list))

GPIO.cleanup()
partnum = "001"
while os.path.isfile(("/home/pi/Experiments/Entrainment/Data/%s_timings_.csv")%(partnum)) == True:
    partnum = '00'+str(int(partnum)+1)
if int(partnum) > 9:
    partnum = '0' + str(int(partnum))

filename    = ("%s_timings_")%(partnum)
filename_part = ("/home/pi/Experiments/Entrainment/Data/%s.csv")%filename

np.savetxt(filename_part, (draw_list, flip_list, wait_list), delimiter=',',fmt="%s")
      
time.sleep(5)
