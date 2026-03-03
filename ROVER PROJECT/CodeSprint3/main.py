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

# # rotation_servo_moteur()




def rotation_servo_moteur2():
    points = []
    pos_y_rover = 0.0 

    while pos_y_rover < 100:
        # Scan à 180° à la position actuelle
        for us in range(1000, 2001, 25):
            d.set_servo_pulse_us(us)
            time.sleep(0.05) 

            echo_time_ms = d.read_sonar_echo_time_ms(pulses=1)
        
            if echo_time_ms is not None:
                distance = (0.34 * echo_time_ms) / 2
            
                angle_rad = ((us - 1500) * 90 / 500) * (pi / 180)
                x = distance * cos(angle_rad)
                y = distance * sin(angle_rad) + pos_y_rover

                points.append((x, y))
                print(f"Pos Y={pos_y_rover:.1f}cm | Angle {us}us : Dist {distance:.2f}m -> ({x:.3f}, {y:.3f})")
        
        # Avancer de 10 cm après le scan
        avancer_de_xcm(150, 25)
        pos_y_rover += 25

    # Sauvegarder les points
    with open("points.txt", "w") as f:
        f.write("[\n " + ",\n ".join(f"({x:.4f}, {y:.4f})" for x, y in points) + "\n]")
    
    return points

# rotation_servo_moteur2()


def verif_obstacle_et_agir(vitesse=150):
    d.set_servo_pulse_us(1500)
    time.sleep(0.2)
    
    while True:
        echo_time_ms = d.read_sonar_echo_time_ms()
        
        if echo_time_ms is not None:
            distance_cm = (0.34 * echo_time_ms / 2) * 100
            print(f"Distance : {distance_cm:.1f} cm")
            
            if distance_cm >= 40:
                print("Chemin libre : Avance...")
                avancer_de_xcm(vitesse, 10) 
            elif distance_cm <=20 :
                print("! OBSTACLE détecté !")
                d.control_motor_speed(0,0,0,0)
                
                print("Déviation par starps...")
                avancer_de_xcm_strap(vitesse,20)
            elif distance_cm>20 and distance_cm < 40:
                print("on tourne")
                tourner(60, vitesse)
        
        time.sleep(0.1) 

# verif_obstacle_et_agir(vitesse=150)
while True:
    d.set_servo_pulse_us(1500)
    time.sleep(0.1)
    echo = d.read_sonar_echo_time_ms(pulses=1)

    if echo:
        print((0.34 * echo / 2) * 100)