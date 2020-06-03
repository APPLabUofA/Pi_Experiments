import time
import RPi.GPIO as GPIO
from random import randint

###initialise pygame###
GPIO.setmode(GPIO.BCM)

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19,18],GPIO.OUT)

###make sure LED is off###
GPIO.output(18,0)

###setup pin for push button###
pin = 26
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

###Setup our function to send triggers###
###trig_type is either 's' or 'r'###
###trig_num must be between 1-15###
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

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###wait for button press to start experiment###
GPIO.wait_for_edge(pin,GPIO.RISING)
time.sleep(1)
GPIO.wait_for_edge(pin,GPIO.RISING)
time.sleep(1)
GPIO.wait_for_edge(pin,GPIO.RISING)

###play countdown###
###flash LED 10 times, with a random delay between each flash###
for i_flash in range(24):
    GPIO.output(18,1)
    GPIO.output(pi2trig(10),1)
    time.sleep(0.1)
    GPIO.output(pi2trig(10),0)
    GPIO.output(18,0)
    time.sleep(randint(100,500)*0.001)

###wait for the other experiment to end (about 8 minutes)###
time.sleep(510)

###flash LED 10 times, with a random delay between each flash###
for i_flash in range(24):
    GPIO.output(pi2trig(11),1)
    GPIO.output(18,1)
    time.sleep(0.1)
    GPIO.output(pi2trig(11),0)
    GPIO.output(18,0)
    time.sleep(randint(100,500)*0.001)

GPIO.output(pi2trig(255),0)
GPIO.cleanup()
