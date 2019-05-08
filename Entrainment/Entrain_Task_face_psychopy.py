import time
import os
from random import randint, shuffle
##import blinkt
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet, local_clock
import RPi.GPIO as GPIO

###initialise pygame###
GPIO.setmode(GPIO.BCM)

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
outlet = StreamOutlet(info)

###setup the display screen and fixation###
mywin = visual.Window([1280, 720], monitor='testMonitor', units='deg', winType='pygame',
                      fullscr=True,color='black')
mywin.mouseVisible = False

stim = visual.ImageStim(win=mywin, image='/home/pi/Experiments/N170/Faces/unfilt_face_01.tiff',pos=(-5,4))

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

for i_blink in range(500):
    stim.draw()
    timestamp = local_clock()
    outlet.push_sample([1], timestamp)
    GPIO.output(pi2trig('s',1),1)
    mywin.flip()
    timestamp = local_clock()
    outlet.push_sample([2], timestamp)
    GPIO.output(pi2trig('r',2),1)
    core.wait(0.5)
    GPIO.output(pi2trig('s',15),0)
    GPIO.output(pi2trig('r',15),0)
    mywin.flip()
    core.wait(0.5)


if os.path.isfile("/home/pi/Experiments/N170/Stop_EEG2.csv") == True:
    core.wait(5)
    os.remove("/home/pi/Experiments/N170/Stop_EEG2.csv")
    core.wait(5)
    os.remove("/home/pi/Experiments/N170/Stop_EEG1.csv")
    
GPIO.cleanup()
mywin.close()
      
time.sleep(5)
