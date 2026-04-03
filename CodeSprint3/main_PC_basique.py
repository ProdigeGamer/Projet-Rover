import socket

HOST = "192.168.4.1"
PORT = 8080

sock = socket.socket()
sock.connect((HOST, PORT))

print("Connecté au rover !")

while True:
    cmd = input("Commande \nz (pour avancer) \n"
    "s (pour reculer) \n" \
    "q (pour tourner à gauche) \n" \
    "d (pour tourner à droite) \n" \
    "x (pour strap) \n" \
    "n (pour stoper le rover de ces morts) \n" 
    "exit (pour stoper la connexion avec le rover) : ")
    if cmd == "quit":
        sock.send(b"exit")
        break

    sock.send(cmd.encode())

sock.close()

