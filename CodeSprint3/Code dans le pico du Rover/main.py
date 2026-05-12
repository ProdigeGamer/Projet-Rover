"""
main_rover_realtime.py  —  À flasher sur le Pico (remplace main.py)
────────────────────────────────────────────────────────────────────
Nouveautés vs main.py :
  • Localisation odométrique temps réel (pos_x, pos_y, heading)
  • Toutes les commandes mettent à jour la position du rover
  • Chaque point sonar est envoyé immédiatement au PC via socket
  • La position du rover est aussi envoyée au PC à chaque mouvement
  • Format des messages : "x=12.5,y=34.2"  (points sonar)
                          "rover_x=10.0,rover_y=5.0,heading=90.0"
"""

import network
import socket
import time
from IPSA_Rover_Lib import IpsaRoverLib
from math import pi, cos, sin

d = IpsaRoverLib()

# ─── Point d'accès Wi-Fi ───────────────────────────────────────────────────────
ap = network.WLAN(network.AP_IF)
ap.config(ssid='Rover De Skandouille', password='skander16')
ap.active(True)
while not ap.active():
    time.sleep(0.1)
print('AP démarré, IP:', ap.ifconfig()[0])

addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(addr)
srv.listen(1)
print('En attente de connexion...')

# ─── État de localisation global ───────────────────────────────────────────────
# pos_x  : profondeur (cm) — axe "avant" du rover
# pos_y  : latéral (cm)    — axe "gauche/droite"
# heading: cap (degrés)    — 0 = face avant, +angle = rotation horaire
pos_x   = 0.0
pos_y   = 0.0
heading = 0.0   # degrés

# ─── Socket courant (rempli à chaque connexion) ────────────────────────────────
conn_global = None

def send_to_pc(msg: str):
    """Envoie une ligne terminée par \\n au PC (non-bloquant)."""
    global conn_global
    if conn_global is None:
        return
    try:
        conn_global.send((msg + '\n').encode())
    except Exception:
        pass  # connexion perdue — on ignore silencieusement

def send_rover_pos():
    """Transmet la position courante du rover au PC."""
    send_to_pc(f"rover_x={pos_x:.2f},rover_y={pos_y:.2f},heading={heading:.1f}")

# ─── Calcul odométrique ────────────────────────────────────────────────────────
WHEEL_DIAMETER_CM = 6.0   # diamètre roue (cm)
MAX_SPEED         = 1000  # valeur speed max dans control_motor_speed

def _speed_to_cm_per_sec(vitesse: int) -> float:
    """Estimation empirique : speed=1000 ≈ 300 RPM."""
    rpm = abs(vitesse) * 300.0 / MAX_SPEED
    return (rpm * pi * WHEEL_DIAMETER_CM) / 60.0

def _move_forward_cm(vitesse: int, distance_cm: float):
    """Avance ou recule de distance_cm, met à jour (pos_x, pos_y)."""
    global pos_x, pos_y
    sign = 1 if vitesse > 0 else -1
    rad  = heading * pi / 180.0
    pos_x += sign * distance_cm * cos(rad)
    pos_y += sign * distance_cm * sin(rad)
    send_rover_pos()

def _rotate_deg(angle_deg: float):
    """Applique une rotation au heading."""
    global heading
    heading = (heading + angle_deg) % 360
    send_rover_pos()

# ─── Mouvements (même API que main.py + mise à jour odométrie) ────────────────
def avancer(vitesse):
    d.control_motor_speed(-vitesse, -vitesse, -vitesse, -vitesse)

def reculer(vitesse):
    d.control_motor_speed(vitesse, vitesse, vitesse, vitesse)

def gauche(vitesse):
    d.control_motor_speed(vitesse, vitesse, -vitesse, -vitesse)

def droite(vitesse):
    d.control_motor_speed(-vitesse, -vitesse, vitesse, vitesse)

def strap(vitesse):
    d.control_motor_speed(vitesse, -vitesse, -vitesse, vitesse)

def stop():
    d.control_motor_speed(0, 0, 0, 0)

def avancer_de_xcm(vitesse, distance):
    """Avance de distance cm, met à jour la position et l'envoie au PC."""
    cm_per_sec      = _speed_to_cm_per_sec(vitesse)
    temps_necessaire = distance / cm_per_sec if cm_per_sec > 0 else 0
    avancer(vitesse)
    time.sleep(temps_necessaire)
    stop()
    _move_forward_cm(vitesse, distance)  # mise à jour odométrie APRÈS le mouvement

def tourner(angles, vitesse):
    """Tourne de angles degrés (+= horaire, -= anti-horaire)."""
    rpm_de_vitesse      = (vitesse * 300) / 1000
    distance_par_minute = rpm_de_vitesse * pi * WHEEL_DIAMETER_CM
    distance_par_seconde = distance_par_minute / 60
    circonference_roue  = pi * WHEEL_DIAMETER_CM
    distance_necessaire = (circonference_roue * abs(angles)) / 52.5
    temps_necessaire    = distance_necessaire / distance_par_seconde if distance_par_seconde > 0 else 0

    if angles >= 0:
        d.control_motor_speed(vitesse, vitesse, -vitesse, -vitesse)
    else:
        d.control_motor_speed(-vitesse, -vitesse, vitesse, vitesse)

    time.sleep(temps_necessaire)
    stop()
    _rotate_deg(angles)   # mise à jour heading

# ─── Scan sonar 180° avec envoi temps réel ────────────────────────────────────
def scan_sonar_et_envoyer(pos_y_rover: float):
    """
    Balaye de 1000 µs à 2000 µs (–90° à +90°).
    Pour chaque point valide : calcule (x, y) dans le repère monde
    et l'envoie immédiatement au PC.
    """
    rad_heading = heading * pi / 180.0

    for us in range(1000, 2001, 25):
        d.set_servo_pulse_us(us)
        time.sleep(0.05)

        echo_time_ms = d.read_sonar_echo_time_ms(pulses=1)
        if echo_time_ms is None:
            continue

        distance = (0.34 * echo_time_ms) / 2  # cm

        # Angle du servo par rapport à l'axe du rover (–90° … +90°)
        angle_servo_rad = ((us - 1500) * 90 / 500) * (pi / 180)

        # Angle absolu dans le repère monde
        angle_monde = rad_heading + angle_servo_rad

        # Coordonnées dans le repère monde (origine = départ du rover)
        x_cm = pos_x + distance * cos(angle_monde)
        y_cm = pos_y + distance * sin(angle_monde)

        send_to_pc(f"x={x_cm:.3f},y={y_cm:.3f}")

def cartographie_realtime():
    """Lance la cartographie complète avec envoi temps réel au PC."""
    global pos_x, pos_y, heading
    pos_x = 0.0
    pos_y = 0.0
    heading = 0.0
    send_rover_pos()  # position initiale

    local_y = 0.0
    while local_y < 100:
        scan_sonar_et_envoyer(local_y)
        avancer_de_xcm(150, 25)
        local_y += 25

    send_to_pc("done=cartographie")

# ─── Boucle serveur ────────────────────────────────────────────────────────────
while True:
    conn_global, client_addr = srv.accept()
    print('Connecté par', client_addr)
    # Envoie la position actuelle dès connexion
    send_rover_pos()

    while True:
        data = conn_global.recv(1024)
        if not data:
            print("Connexion fermée")
            break

        data = data.strip().decode(errors="replace")
        print("Reçu :", data)

        if data == "z":
            avancer(50)

        elif data == "s":
            reculer(50)

        elif data == "q":
            gauche(50)

        elif data == "d":
            droite(50)

        elif data == "x":
            strap(50)

        elif data == "n":
            stop()

        # ── Nouvelles commandes structurées (depuis rover_gui.py) ──────────────
        elif data.startswith("avancer:"):
            # format : avancer:vitesse:duree_s  ou  avancer:-vitesse:duree_s
            parts = data.split(":")
            try:
                v = int(parts[1])
                t = float(parts[2])
                cm_per_sec = _speed_to_cm_per_sec(abs(v))
                dist = cm_per_sec * t
                if v >= 0:
                    avancer_de_xcm(v, dist)
                else:
                    avancer_de_xcm(-v, dist)   # recule
                    _move_forward_cm(v, dist)  # ajuste direction
            except Exception as e:
                print("Erreur avancer:", e)

        elif data.startswith("tourner:"):
            # format : tourner:angle:vitesse
            parts = data.split(":")
            try:
                angle = float(parts[1])
                vit   = int(parts[2])
                tourner(angle, vit)
            except Exception as e:
                print("Erreur tourner:", e)

        elif data == "start":
            cartographie_realtime()

        elif data == "stop":
            stop()

        elif data == "exit":
            stop()
            break

        else:
            print("Commande inconnue:", data)

    conn_global = None
