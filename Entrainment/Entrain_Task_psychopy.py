import time
import os
from random import randint, shuffle
##import blinkt
from psychopy import visual, core, event
import RPi.GPIO as GPIO

###initialise pygame###
GPIO.setmode(GPIO.BCM)

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

###setup the display screen and fixation###
mywin = visual.Window([1280, 720], monitor='testMonitor', units='deg', winType='pygame',
                      fullscr=True,color='black')
mywin.mouseVisible = False

stim = visual.Rect(win=mywin, width=5,height=5,pos=(-10,5),fillColor='white')
rect_size = 100
rect_green = (0,255,0)
rect_blue = (0,0,255)

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

###define led strip object, set brightness, set LEDs to zero in case they are on###
##blinkt.clear()
##blinkt.show()

event.waitKeys()

for i_blink in range(300):
    GPIO.output(pi2trig('s',1),1)
    stim.draw()
    GPIO.output(pi2trig('s',2),1)
    mywin.flip()
    GPIO.output(pi2trig('s',3),1)
    core.wait(0.5)
    mywin.flip()
    GPIO.output(pi2trig('s',15),0)
    core.wait(0.5)


GPIO.cleanup()
      
time.sleep(5)
