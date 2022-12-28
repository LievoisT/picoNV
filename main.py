from machine import Pin, Timer
import select
import sys
import utime


def tick(_tick):
    global led
    global ledToggle

    if ledToggle:
        led.value(not led.value())
    else:
        led.value(False)


led = Pin(25, Pin.OUT)
ledToggle = True
# noinspection PyArgumentList
timer = Timer()
timer.init(period=1000, mode=Timer.PERIODIC, callback=tick)

relay = Pin(6, Pin.OUT)  # set pin as output
while True:
    if select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.readline()
        if ch[0] == '1':
            print('Starting wiper')
            relay(1)
            utime.sleep(3)
            relay(0)
        elif ch[0] == '2':
            ledToggle = False
        elif ch[0] == '3':
            ledToggle = True

    else:
        utime.sleep(1)
