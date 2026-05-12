import network
import socket
import time
from IPSA_Rover_Lib import IpsaRoverLib
from math import pi

d = IpsaRoverLib()


ap = network.WLAN(network.AP_IF)
ap.config(ssid='Rover De Skandouille', password='skander16')
ap.active(True)

while not ap.active():
    time.sleep(0.1)

print('AP démarré, IP:', ap.ifconfig()[0])  

addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('En attente de connexion...')

def avancer(vitesse):
    print("Avancer")
    d.control_motor_speed(-vitesse, -vitesse, -vitesse, -vitesse)

def reculer(vitesse):
    print("Reculer")
    d.control_motor_speed(vitesse, vitesse, vitesse, vitesse)

def gauche(vitesse):
    print("Gauche")
    d.control_motor_speed(vitesse, vitesse, -vitesse, -vitesse)

def droite(vitesse):
    print("Droite")
    d.control_motor_speed(-vitesse, -vitesse, vitesse, vitesse)

def strap(vitesse):
    print("strap")
    d.control_motor_speed(vitesse, -vitesse, -vitesse, vitesse)

def stop():
    print("STOP")
    d.control_motor_speed(0, 0, 0, 0)

def cartographie():
    points = []
    pos_y_rover = 0.0 

    while pos_y_rover < 100:

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
        
        avancer_de_xcm(150, 25)
        pos_y_rover += 25

    with open("points.txt", "w") as f:
        f.write("[\n " + ",\n ".join(f"({x:.4f}, {y:.4f})" for x, y in points) + "\n]")
    
    return points




while True:
    conn, client_addr = s.accept()
    print('Connecté par', client_addr)


    while True:
        data = conn.recv(1024)

        if not data:
            print("Connexion fermée")
            break

        print("Reçu brut :", data)

        data = data.strip()
        print("Après strip :", data)

        if data == b"z":
            print("Commande : Avancer")
            avancer(50)

        elif data == b"s":
            print("Commande : Reculer")
            reculer(50)

        elif data == b"q":
            print("Commande : Gauche")
            gauche(50)

        elif data == b"d":
            print("Commande : Droite")
            droite(50)

        elif data == b"x":
            print("Commande : Strap")
            strap(50)

        elif data == b"n":
            print("Commande : STOP")
            stop()

        elif data == b"exit":
            print("Commande : EXIT")
            stop()
            break

        else:
            print("Commande inconnue")

