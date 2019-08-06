import time
import os
from random import randint
from random import shuffle
import neopixel
import RPi.GPIO as GPIO
import datetime
import numpy
import pygame

###setup GPIO pins and initialise pygame###
GPIO.setmode(GPIO.BCM)
##############THIS BREAKS THE LEDs FOR SOME REASON
#pygame.init()
##############DO NOT ENEABLE
pygame.display.init()

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19,18],GPIO.OUT)

###setup pin for push button###
pin = 21
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

###variables for filenames and save locations###
partnum = '001'
device = 'Amp'
filename = 'Visual_P3_LED_old_neopixel'
exp_loc = 'Visual_P3_LED_old_neopixel'
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

###LED variables###
LED_COUNT   = 6       # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)

###define the number of trials, and tones per trial###
trials = 10
low_rate = 0.8
high_rate = 0.2
low_tone = numpy.zeros(trials*low_rate)
high_tone = numpy.ones(trials*high_rate)
low_tone_list = low_tone.tolist()
high_tone_list = high_tone.tolist()
tones = low_tone_list + high_tone_list
shuffle(tones)

###setup variables to record times###
trig_time   = []
trig_type = []
delay_length  = []
resp_time = []

###set triggers to 0###
GPIO.output(pi2trig(255),0)

###define led strip object, set brightness, set LEDs to zero in case they are on###
strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
strip.begin()
strip.setBrightness(127)

for i_strip in range(6):
        strip.setPixelColorRGB(i_strip,0,0,0)
strip.show()

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)

###draw fixation###
pygame.draw.line(screen, (255, 255, 255), (x_center-10, y_center), (x_center+10, y_center),4)
pygame.draw.line(screen, (255, 255, 255), (x_center, y_center-10), (x_center, y_center+10),4)
pygame.display.flip()
time.sleep(10)

###wait for button press to start experiment###
#GPIO.wait_for_edge(21,GPIO.RISING)
start_exp = time.time()
GPIO.output(pi2trig(5),1)
for i_strip in range(6):
        strip.setPixelColorRGB(i_strip,0,127,0)
strip.show()
time.sleep(5)
GPIO.output(pi2trig(5),1)
time.sleep(5)

for i_tone in range(len(tones)):
        delay = ((randint(0,500))*0.001)+1.00
        delay_length.append(delay)
        if tones[i_tone] == 0:#standard
                ###set LEDs as green###
                for i_strip in range(6):
                        strip.setPixelColorRGB(i_strip,127,0,0)
                trig = 1
        elif tones[i_tone] == 1:#targets
                ###set LEDs as blue###
                for i_strip in range(6):
                        strip.setPixelColorRGB(i_strip,0,0,127)
                trig = 2
                trig_type.append(trig)
                GPIO.output(pi2trig(trig),1)
                trig_time.append(time.time() - vid_start)
                strip.show()
                ###now try and get a response###
                start_resp = time.time()
                wait_resp = 0
                edge_detect = GPIO.wait_for_edge(pin,GPIO.RISING, timeout = 1000)
                if edge_detect is not None:
                        GPIO.output(pi2trig(255),0)
                        resp = time.time() - start_resp
                        resp_time.append(resp)
                        GPIO.output(pi2trig(int(tones[i_tone])+3),1)
                        time.sleep(1000 - (resp*1000))
                        wait_resp = 1
                GPIO.output(pi2trig(255),0)
                for i_strip in range(6):
                        strip.setPixelColorRGB(i_strip,0,0,0)
                ###update LEDs###
                strip.show()
                edge_detect = GPIO.wait_for_edge(pin,GPIO.RISING, timeout = 1000)
                if edge_detect is not None and wait_resp == 0:
                        GPIO.output(pi2trig(255),0)
                        resp = time.time() - start_resp
                        resp_time.append(resp)
                        GPIO.output(pi2trig(int(tones[i_tone])+3),1)
                        time.sleep(1000 - (resp*1000))
                        wait_resp = 1
                else:
                        resp_time.append(0)
                ###wait for a random amount of time###
                time.sleep(delay)

##GoPro_LED_Flash(10)
###show the end screen###
GPIO.output(pi2trig(6),1)
time.sleep(0.5)
GPIO.output(pi2trig(255),0)
time.sleep(0.5)

###save times###
while os.path.isfile("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/Trial_Information/" + partnum + "_" + filename + ".csv") == True:
    if int(partnum) >= 9:
        partnum = "0" + str(int(partnum) + 1)
    else:
        partnum = "00" + str(int(partnum) + 1)

filename_part = ("/home/pi/research_experiments/Experiments/" + exp_loc + "/Data/" + device + "/Trial_Information/" + partnum + "_" + filename + ".csv")

the_list = [date, trig_type,trig_time,delay_length,resp_time]
df_list = pd.DataFrame({i:pd.Series(value) for i, value in enumerate(the_list)})
df_list.columns = ['Date','Trigger_Type','Trigger_Onset_Time','Trial_Delay','Response_Time']
df_list.to_csv(filename_part)

GPIO.output(pi2trig(255),0)
pygame.display.quit()
pygame.quit()
GPIO.cleanup()

if os.path.isfile("/home/pi/research_experiments/Stop_EEG2.csv") == True:   
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG2.csv")
    time.sleep(5)
    os.remove("/home/pi/research_experiments/Stop_EEG1.csv")
