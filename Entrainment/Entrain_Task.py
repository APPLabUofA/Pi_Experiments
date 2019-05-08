import time
import os
from random import randint, shuffle
##import blinkt
import pygame
import RPi.GPIO as GPIO

###initialise pygame###
pygame.init()
pygame.display.init()
GPIO.setmode(GPIO.BCM)

###setup pins for triggers###
GPIO.setup([4,17,27,22,5,6,13,19],GPIO.OUT)

###setup the display screen and fixation###
pygame.mouse.set_visible(0)
disp_info = pygame.display.Info()
screen = pygame.display.set_mode((disp_info.current_w, disp_info.current_h),pygame.FULLSCREEN)
x_center = disp_info.current_w/2
y_center = disp_info.current_h/2
black = pygame.Color(0, 0, 0)
white = pygame.Color(255,255,255)
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

key_pressed = 0
pygame.event.clear()
while key_pressed == 0:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            key_pressed = 1

for i_blink in range(300):
##    blinkt.set_pixel(0,255,255,255)
    pygame.draw.rect(screen, white , (0,0,rect_size,rect_size))

##    blinkt.show()
    GPIO.output(pi2trig('s',1),1)
    pygame.display.flip()
    time.sleep(0.5)
##    blinkt.clear()
##    blinkt.show()
    screen.fill(pygame.Color("black"))
    pygame.display.flip()
    GPIO.output(pi2trig('s',1),0)
    time.sleep(0.5)


GPIO.cleanup()
      
time.sleep(5)
