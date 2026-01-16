from machine import I2C, Pin
import time
import motor_driver_lib as motor

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=200000)
motor.init_i2c(i2c)
motor.set_motor_parameters()


def test1():
    motor.control_motor_pwm(700, 1500, 0, 0)
    time.sleep(2)
    motor.control_motor_pwm(0, 0, 0, 0)