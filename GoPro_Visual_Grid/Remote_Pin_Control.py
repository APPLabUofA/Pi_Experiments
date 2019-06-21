# https://gpiozero.readthedocs.io/en/stable/remote_gpio.html
# raspberrypi.org/documentation/configuration/wireless/access-point.md
from gpiozero import LED
from gpiozero import *
from gpiozero.pins.pigpio import PiGPIOFactory
import time
from time import sleep
import numpy as np
import neopixel
import board

# run with command 'GPIOZERO_FACTORY=pigpio PIGPIO_ADDR=192.168.4.2 python3 Remote_Pin_Control.py'

length = 5
local_pi_trigs = np.zeros((length))
start_time = time.time()

partnum = input("partnum: ")
#factory = PiGPIOFactory(host='192.168.4.2') # host='129.128.174.163'
led = LED(17) #,pin_factory=factory
#self.neo_remo = PWMLED(18)
#length = 200
pin_num = 6
pin_out = board.D18
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
blank = (0, 0, 0)
brightness = 0.2

#LED_COUNT     = 6
#LED_PIN       = 18
#LED_FREQ_HZ   = 800000
#LED_DMA       = 5
#LED_INVERT    = False

def flippy(strip, colour):
    for i in range(strip.numPixels()):
        strip.setPixelsColor(i,colour)
        strip.show()
        
#strip = neopixel.NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
strip = neopixel.NeoPixel(pin_out, pin_num, brightness = brightness, auto_write = True)

#strip.begin() # pin_factory=factory

#flippy(strip, (255,255,255))
strip.fill(red)

for i in range(length):
    local_pi_trigs[i] = time.time() - start_time 
    print(time.time() - start_time)
    led.on()
    strip.fill(blue)
    sleep(1)
    strip.fill(blank)
    led.off()
    sleep(1)

###save trial information###
filename = "test"
filename_part = ("/home/pi/Documents/GitHub/GoPro_Grid_Pi/Pi3_Amp_Latencies/Pi_Times/" + partnum + "_" + filename + ".csv")


np.savetxt(filename_part, (local_pi_trigs), delimiter=',',fmt="%s")
