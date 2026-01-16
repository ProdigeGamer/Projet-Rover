from machine import Pin
from time import sleep

led = Pin("LED", Pin.OUT)
i = 0
while i < 9000 :
    led.toggle()
    sleep(0.25)
    i+=1
