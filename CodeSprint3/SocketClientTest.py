import socket 

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect(('10.9.160.191', 444))
print("Connected! ")

while True:
    da = input("Data à envoyer: ").encode()
    socket.send(da)
    if da == b"q":
        break

socket.close()




