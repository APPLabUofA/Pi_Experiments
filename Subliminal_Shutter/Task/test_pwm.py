import pigpio
import time

pi = pigpio.pi()

pi.hardware_PWM(18, 15, 500000)
