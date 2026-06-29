from machine import Pin, Timer
from PCA9685 import PCA9685
import select
import sys
import utime

# --- Waveshare Motor Driver Setup ---
# The Waveshare board uses a PCA9685 chip over I2C to control a TB6612FNG motor driver
pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(50)

class MotorDriver:
    def __init__(self):
        # I2C channel mappings for the Waveshare Hat
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4

    def MotorRun(self, motor, forward, speed):
        # Speed must be between 0 and 100
        if speed > 100: speed = 100
        
        if motor == 0: # Motor A (Wiper Power)
            pwm.setDutycycle(self.PWMA, speed)
            if forward:
                pwm.setLevel(self.AIN1, 0)
                pwm.setLevel(self.AIN2, 1)
            else:
                pwm.setLevel(self.AIN1, 1)
                pwm.setLevel(self.AIN2, 0)
        else: # Motor B (Lambertian Target)
            pwm.setDutycycle(self.PWMB, speed)
            if forward:
                pwm.setLevel(self.BIN1, 0)
                pwm.setLevel(self.BIN2, 1)
            else:
                pwm.setLevel(self.BIN1, 1)
                pwm.setLevel(self.BIN2, 0)

    def MotorStop(self, motor):
        if motor == 0:
            pwm.setDutycycle(self.PWMA, 0)
        else:
            pwm.setDutycycle(self.PWMB, 0)

board = MotorDriver()

# --- Hardware Initialization ---

def tick(_tick):
    global led, ledToggle
    if ledToggle:
        led.value(not led.value())
    else:
        led.value(0)

# Onboard LED Heartbeat
led = Pin(25, Pin.OUT)
ledToggle = True
timer = Timer()
timer.init(period=1000, mode=Timer.PERIODIC, callback=tick)

# 1. Wiper Setup (Motor A)
# Turn on power to Motor A and leave it running at 100% speed.
board.MotorRun(0, True, 100) 

# The actual wiper movement is gated by GP2
wiper_trigger = Pin(2, Pin.OUT)
wiper_trigger.value(0)

# 2. Lambertian Target Setup (Motor B)
# Active-Low Hall sensors (use internal PULL_UP resistors)
hall_in = Pin(19, Pin.IN, Pin.PULL_UP)
hall_out = Pin(20, Pin.IN, Pin.PULL_UP)

print("System Ready.")
print("Commands: 1=Wiper, 2=LED Off, 3=LED On, 4=Target In, 5=Target Out")

while True:
    if select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.readline().strip() 
        
        if not ch:
            continue
            
        if ch[0] == '1':
            print('Starting wiper (GP2)')
            wiper_trigger.value(1)
            utime.sleep(3)
            wiper_trigger.value(0)
            
        elif ch[0] == '2':
            ledToggle = False
            
        elif ch[0] == '3':
            ledToggle = True
            
        elif ch[0] == '4':
            print('Moving Lambertian Target IN...')
            # Motor 1 is Motor B on the board. True = forward.
            board.MotorRun(1, True, 100)
            
            # 15-second timeout safeguard (6 RPM = 10s per full rotation)
            timeout = utime.ticks_ms() + 15000 
            while hall_in.value() == 1 and utime.ticks_diff(timeout, utime.ticks_ms()) > 0:
                utime.sleep_ms(50)
                
            board.MotorStop(1)
            if hall_in.value() == 1:
                print('Timeout: Target IN magnet not detected!')
            else:
                print('Target reached IN position.')

        elif ch[0] == '5':
            print('Moving Lambertian Target OUT...')
            # Moving forward continuously to cycle to the OUT position
            board.MotorRun(1, True, 100)
            
            timeout = utime.ticks_ms() + 15000
            while hall_out.value() == 1 and utime.ticks_diff(timeout, utime.ticks_ms()) > 0:
                utime.sleep_ms(50)
                
            board.MotorStop(1)
            if hall_out.value() == 1:
                print('Timeout: Target OUT magnet not detected!')
            else:
                print('Target reached OUT position.')

    else:
        utime.sleep(1)