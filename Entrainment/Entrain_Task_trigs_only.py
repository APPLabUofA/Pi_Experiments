import time
import os
from random import randint, shuffle
import RPi.GPIO as GPIO

###initialise pygame###
GPIO.setmode(GPIO.BCM)

###setup pins for triggers###
GPIO.setup(26,GPIO.OUT)

###set triggers to 0###
GPIO.output(26,0)

###define led strip object, set brightness, set LEDs to zero in case they are on###

for i_blink in range(300):
    GPIO.output(26,1)
    time.sleep(0.1)
    GPIO.output(26,0)
    time.sleep(0.1)


GPIO.cleanup()
