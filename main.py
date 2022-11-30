from machine import Pin, Timer
import select
import sys
import utime


def tick(_tick):
    global led

    led.value(not led.value())


led = Pin(25, Pin.OUT)
# noinspection PyArgumentList
timer = Timer()
timer.init(period=1000, mode=Timer.PERIODIC, callback=tick)

relay = Pin(6, Pin.OUT)  # set pin as output
while True:
    if select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.readline()
        if ch[0] == "1":
            print('Starting wiper')
            relay(1)
            utime.sleep(3)
            relay(0)

    else:
        utime.sleep(1)
