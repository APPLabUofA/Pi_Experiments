from psychopy import prefs
import RPi.GPIO as GPIO

###setup psychopy###
prefs.general['audioLib'] = ['pygame']

from psychopy import sound
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

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

GPIO.output(pi2trig('s',15),0)
GPIO.output(pi2trig('r',15),0)

tone = sound.Sound('/home/pi/Experiments/Auditory_Bird_Oddball/Task/Sounds/alt_bird_03.wav', sampleRate=44100, bits=8)
tone.setVolume(25)

for i_trial in range(3):
    GPIO.output(pi2trig('s',1),1)
    tone.play()
    GPIO.output(pi2trig('s',2),2)
    time.sleep(0.5)
    GPIO.output(pi2trig('s',15),0)
    time.sleep(0.5)


##import pygame
##import time
##
##pygame.mixer.pre_init(44100,-16,2,1024)
##pygame.init()
##pygame.mixer.init()
##pygame.mixer.music.load('/home/pi/Experiments/Sounds/high_tone.wav')
##
##for i_trial in range(10):
##    pygame.mixer.music.play()
##    time.sleep(0.5)

#####here we will test the drawing time of psychopy###
##from psychopy import visual, core
##
##mywin = visual.Window([592,448], monitor='testMonitor', units='deg', winType='pygame',fullscr=False)
##
##stim_numbers = visual.TextStim(win=mywin,text='2',pos=(0,0), height=2)
##
##stim_letters = visual.TextStim(win=mywin,text='a',pos=(0,0), height=2)
##
##stim_triangles = visual.ShapeStim(win=mywin, fillColor='white', vertices=[(-2, -2),(0, 2),(2, -2)])
##
##for i_trial in range(10):
##    stim_numbers.draw()
##    start_draw = core.getTime()
##    mywin.flip()
##    print(core.getTime()-start_draw)
##    core.wait(0.5)
##    mywin.flip()
##    core.wait(0.5)
    
