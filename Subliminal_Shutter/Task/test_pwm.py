import os

os.system('sudo pigpiod')

import pigpio
import RPi.GPIO as GPIO
import time

pi = pigpio.pi()
GPIO.setmode(GPIO.BCM)
GPIO.setup([4,17,27,22,5,6,13,19,23,24],GPIO.OUT)
GPIO.output(4,1)

pi.hardware_PWM(18, 17, 333333)

time.sleep(5)

GPIO.output(4,0)

pi.hardware_PWM(18, 17, 666666)

time.sleep(5)

pi.hardware_PWM(18, 17, 900000)

time.sleep(5)

pi.hardware_PWM(18, 17, 0)

pi.stop()

os.system(' sudo killall pigpiod')
