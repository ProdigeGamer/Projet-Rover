# rover_network.py
import network
import socket
import _thread
from collections import deque

class IpsaRoverNetwork:
    """
    Gère la communication Wi-Fi du rover en arrière-plan (cœur 1).
    
    Usage minimal :
        net = IpsaRoverNetwork('Rover-01', 'rover1234')
        net.start()
        net.send("distance", 42)        # envoie une valeur
        net.send({"x": 1, "y": 2})      # envoie plusieurs valeurs
        msg = net.receive()             # lit un message venu du PC
    """

    def __init__(self, ssid: str, password: str, port: int = 8080):
        self.ssid     = ssid
        self.password = password
        self.port     = port
        self._inbox   = deque((), 20)
        self._outbox  = deque((), 20)
        self._lock    = _thread.allocate_lock()

    def start(self):
        """Démarre le réseau sur le cœur 1. À appeler une seule fois."""
        _thread.start_new_thread(self._network_task, ())

    def send(self, key_or_dict, value=None):
        """
        Envoie une ou plusieurs données au PC.

        Exemples :
            net.send("distance", 42)
            net.send("message", "obstacle détecté")
            net.send({"vitesse": 50, "cap": 180, "distance": 30})
        """
        if isinstance(key_or_dict, dict):
            payload = ",".join(f"{k}={v}" for k, v in key_or_dict.items())
        else:
            payload = f"{key_or_dict}={value}"
        with self._lock:
            self._outbox.append(payload)

    def receive(self):
        """
        Retourne le prochain message envoyé par le PC, ou None.
        
        Exemple :
            msg = net.receive()
            if msg:
                print("PC dit :", msg)
        """
        with self._lock:
            return self._inbox.popleft() if self._inbox else None


    def _network_task(self):
        # Démarrage de l'AP
        ap = network.WLAN(network.AP_IF)
        ap.config(ssid=self.ssid, password=self.password)
        ap.active(True)
        while not ap.active():
            pass
        print(f"[NET] AP '{self.ssid}' démarré — IP : {ap.ifconfig()[0]}")

        # Serveur TCP
        srv = socket.socket()
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(socket.getaddrinfo('0.0.0.0', self.port)[0][-1])
        srv.listen(1)
        print(f"[NET] En écoute sur le port {self.port}...")

        while True:
            conn, addr = srv.accept()
            conn.settimeout(0.5)
            print(f"[NET] PC connecté : {addr}")

            while True:
                # Réception
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    with self._lock:
                        self._inbox.append(data.decode().strip())
                except OSError:
                    pass  # timeout → pas de données, on continue

                # Envoi
                with self._lock:
                    while self._outbox:
                        msg = self._outbox.popleft()
                        try:
                            conn.send((msg + '\n').encode())
                        except OSError:
                            break

            conn.close()
            print("[NET] PC déconnecté, en attente...")