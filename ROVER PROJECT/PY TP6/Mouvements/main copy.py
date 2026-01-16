import math  # notre module de logging
import os
from machine import I2C, Pin
import time
import motor_driver_lib as motor

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=200000)
motor.init_i2c(i2c)
motor.set_motor_parameters()


def forward(duree, vitesse):
    pwm_value = motor.voltage_to_pwm(vitesse)
    motor.control_motor_pwm(-pwm_value, -pwm_value, -pwm_value, -pwm_value)
    time.sleep(duree)
    motor.control_motor_pwm(0, 0, 0, 0)
    print("Mouvement en avant effectué.")

def downward(duree, vitesse):
    pwm_value = motor.voltage_to_pwm(vitesse)
    motor.control_motor_pwm(pwm_value, pwm_value, pwm_value, pwm_value)
    time.sleep(duree)
    motor.control_motor_pwm(0, 0, 0, 0)
    print("Mouvement en arrière effectué.")

def right (duree, vitesse):
    pwm_value = motor.voltage_to_pwm(vitesse)
    motor.control_motor_pwm(pwm_value, -pwm_value, -pwm_value, pwm_value)
    time.sleep(duree)
    motor.control_motor_pwm(0, 0, 0, 0)
    print("Mouvement à droite effectué.")   

def turnright(duree, vitesse):
    pwm_value = motor.voltage_to_pwm(vitesse)
    motor.control_motor_pwm(pwm_value, pwm_value, -pwm_value, -pwm_value)
    time.sleep(duree)
    motor.control_motor_pwm(0, 0, 0, 0)
    print("Rotation à droite effectuée.")

def stop():
    motor.control_motor_pwm(0, 0, 0, 0)
    print("Arrêt des moteurs.")


def danse(time):
    forward(time, 2)
    turnright(time, 2)
    downward(time, 2)
    right(time, 2)
    stop()
    print("Danse terminée.")

forward(3, 5)