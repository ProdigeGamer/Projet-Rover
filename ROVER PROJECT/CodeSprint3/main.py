from IPSA_Rover_Lib import IpsaRoverLib
import time 
from math import pi
from math import pi, cos, sin
import time
d = IpsaRoverLib()

def avancer(vitesse,temps):
    d.control_motor_speed(-vitesse,-vitesse,-vitesse,-vitesse)
    time.sleep(temps)
    d.control_motor_speed(0,0,0,0)

def avancer_strap(vitesse,temps):
    d.control_motor_speed(vitesse,-vitesse,-vitesse,vitesse)
    time.sleep(temps)
    d.control_motor_speed(0,0,0,0)

def avancer_de_xcm(vitesse,distance):
    rpm_de_vitesse = (vitesse*300)/1000
    distance_par_mintue = (rpm_de_vitesse * pi *6)
    distance_par_seconde = distance_par_mintue /60
    temps_necessaire = distance / distance_par_seconde
    avancer(vitesse,temps_necessaire)



def tourner(angles,vitesse):
    rpm_de_vitesse = (vitesse*300)/1000
    distance_par_mintue = (rpm_de_vitesse * pi *6)
    distance_par_seconde = distance_par_mintue /60
    circonference_roue = pi * 6
    distance_necessaire = (circonference_roue * angles) / 52.5 #52.5 est la valeur visuel de coeff pour faire un tour complet
    temps_necessaire = distance_necessaire / distance_par_seconde
    d.control_motor_speed(vitesse,vitesse,-vitesse,-vitesse)
    time.sleep(temps_necessaire)
    d.control_motor_speed(0,0,0,0)


def avancer_de_xcm_strap(vitesse,distance):
    rpm_de_vitesse = (vitesse*300)/1000
    distance_par_mintue = (rpm_de_vitesse * pi *6)
    distance_par_seconde = distance_par_mintue /60
    temps_necessaire = distance / distance_par_seconde
    avancer_strap(vitesse,temps_necessaire)


#avancer_de_xcm_strap(150,100)


def rotation_servo_moteur():
    for us in range(1000,2000,50):
        d.set_servo_pulse_us(us)
        time.sleep(.1)

    #Sonar

    for mes in range(10):
        echo_time_ms = d.read_sonar_echo_time_ms()
        if echo_time_ms is None:
            continue
        distance = 0.34*echo_time_ms
        print(f"Distance mesurée par le sonar : {distance/2} m donc {distance*100/2} cm")
        print(f"Temps de vol de l'onde : {echo_time_ms}")
        time.sleep(.5)

# rotation_servo_moteur()

def scan_180():
    points = []
    pos_y_rover = 0.0  
    for us in range(1000, 2000, 25):  
        d.set_servo_pulse_us(us) 
        time.sleep(0.05)

        echo_time_ms = d.read_sonar_echo_time_ms()
        if echo_time_ms is None:
            avancer_de_xcm(150, 10)
            pos_y_rover += 0.10
            continue
        distance = (0.34 * echo_time_ms) / 2
        
        angle_rad = ((us - 1500) * 90 / 500) * (pi / 180)


        x_relatif = distance * cos(angle_rad)
        y_relatif = distance * sin(angle_rad) 

        x_global = x_relatif
        y_global = y_relatif + pos_y_rover

        points.append((x_global, y_global))

        print(f"Rover à Y={pos_y_rover:.2f}m | Point: ({x_global:.2f}, {y_global:.2f})")
        
        avancer_de_xcm(150, 10) 
        pos_y_rover += 0.10 

    formatted_points = "[\n " + ",\n ".join(f"({x}, {y})" for x, y in points) + "\n]"
    with open("points.txt", "w") as f:
        f.write(formatted_points)



scan_180()