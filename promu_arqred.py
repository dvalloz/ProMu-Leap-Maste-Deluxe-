#--------- PARTE ARQRED ------------------------------------
import json
from socket import *
dir_IP_servidor= '158.42.188.200'
puerto_servidor = 64010
dir_socket_servidor =(dir_IP_servidor, puerto_servidor)
s = socket(AF_INET, SOCK_STREAM)# IPv4, TCP
s.connect(dir_socket_servidor)

def comprobar_respuesta(respuesta):
    if respuesta.split()[0]!= '400':
        return True
    else:
        return False
    
def enviar_hello():
    # Obtener el nombre de host de la máquina local
    hostname = gethostname()
    # Obtener la dirección IP correspondiente al nombre de host
    direccion_IP_cliente = gethostbyname(hostname)
    mensaje_hello= 'HELLO'+' '+direccion_IP_cliente+'\r\n'
    s.send(mensaje_hello.encode())
    mensaje_rx = s.recv(2048)     
    

def enviar_user(username):
    mensaje_user= 'USER'+' '+username+'\r\n'
    s.send(mensaje_user.encode())
    mensaje_rx = s.recv(2048)
    if  not comprobar_respuesta(mensaje_rx.decode()):
        # ENviar mensaje de que el usuario no es correcto y ha de cambiarse    
    else:
        return mensaje_rx.decode()

        
    
def enviar_pass(passnumber):
    mensaje_pass= 'PASS'+' '+passnumber+'\r\n'
    s.send(mensaje_pass.encode())
    mensaje_rx = s.recv(2048)
    if  not comprobar_respuesta(mensaje_rx.decode()):
        return False
    else:
        return  True
       

    
    
def enviar_getleaderboard():
    mensaje_getleaderboard= 'GET_LEADERBOARD'+'\r\n'
    while True:
        mensaje_rx = s.recv(2048)
        if mensaje_rx.decode().split()[0]== '200' or mensaje_rx.decode().split()[0]== '202':
            print(mensaje_rx.decode())
            if mensaje_rx.decode().split()[0]== '202':
                break
        else:
            salto=json.loads(mensaje_rx)
            print(salto["ranking"],salto["nombre"],salto["grupo_ProMu"],salto["altura"],salto["fecha"])
       
 
def enviar_data(nombre, grupo, altura, fecha):
    data= json.dumps({'nombre':nombre,'grupo_ProMu':grupo,'altura': altura,'fecha':fecha})
    mensaje_data= 'SEND_DATA '+ data+ '\r\n'
    while True:
        s.send(mensaje_data.encode())
        mensaje_rx = s.recv(2048)
        if comprobar_respuesta(mensaje_rx.decode()):
            print(mensaje_rx.decode())
            break
        else:
            # Enviar mensaje de error 
    
def enviar_quit():
    mensaje_quit='QUIT'+'\r\n'
    s.send(mensaje_quit.encode())
   
        

#----------------------------------------------------------------------------------
    
def iniciar_sesion():