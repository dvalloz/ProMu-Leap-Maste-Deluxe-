from guizero import App, Text, TextBox, PushButton, Picture, Combo, Window, Box
import os
import webbrowser

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
        return False 
    else:
        return True
 
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
    leaderboard=''
    s.send(mensaje_getleaderboard.encode())
    while True:
        mensaje_rx = s.recv(2048)
        if mensaje_rx.decode().split()[0]== '200' or mensaje_rx.decode().split()[0]== '202':
            if mensaje_rx.decode().split()[0]== '202':
                break
        else:
            salto=json.loads(mensaje_rx)
            cadena="Top "+str(salto["ranking"])+' '+salto["nombre"]+' '+salto["grupo_ProMu"]+' '+ str(salto["altura"])+'mm '+salto["fecha"]
            leaderboard= leaderboard+cadena+' \n'
    return leaderboard
       
 
def enviar_data(nombre, grupo, altura, fecha):
    data= json.dumps({'nombre':nombre,'grupo_ProMu':grupo,'altura': altura,'fecha':fecha})
    mensaje_data= 'SEND_DATA '+ data+ '\r\n'
    s.send(mensaje_data.encode())
    mensaje_rx = s.recv(2048)
    if mensaje_rx.decode().split()[0]== '200':
        return True
    else:
        return False
        
     
            
    
def enviar_quit():
    mensaje_quit='QUIT'+'\r\n'
    s.send(mensaje_quit.encode())
   
        

#----------------------------------------------------------------------------------
 #PARTE FISICA-MATES
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
import numpy as np
from scipy.ndimage import gaussian_filter1d as gf

def primitivaNumerica(variable, tiempo, y0):
    return cumtrapz(variable,x=tiempo,initial=y0)

g=9.81

def sacar_datos(nombre_fichero):
    global t,av_g,av
    fichero= nombre_fichero
    df=pd.read_excel(fichero)

    t=df.values[:,0].astype(float)

    a=df.values[:,1].astype(float)
    ay=df.values[:,3].astype(float)

    av=a*np.sign(ay)

    a_g=a-g
    av_g=av-g
    
    return t, av_g, av

def calcular_parametros( t, av_g, av, m ):
    global y_gauss, F,Fmax,P,d
    #Aceleracion suavizada
    y_gauss = gf(av_g, 5)

    #Fuerza al dar el salto
    F=av*m
    #Fuerza maxima
    Fmax=np.max(F)
    #Velocidad
    v=primitivaNumerica(y_gauss,t,0)
    #Desplazamiento
    d=primitivaNumerica(v,t,0)
    #Velocidad Maxima
    global v0,maximos,minimos,maximos1,minimos1
    v0=v.max()

    maximos = np.argmax(v)
    minimos = np.argmin(v)
    
    #Final del impulso
    tfi= t[maximos]
    #Final del vuelo
    tfv= t[minimos]
    #Duracion del tiempo de vuelo
    T=tfv-tfi
    
    #Potencia
    P=F*v
    #Potencia máxima
    Pmax= P.max()
    #Potencia normalizada
    Pn=Pmax/m
    
    #Altura del salto a partir de v0 (en cm)
    H=v0**2/2*g
    
    #Altura del salto a partir de T
    H2=g*T**2/8



    return H, Pmax, v, y_gauss, F

def graf_a():
    plt.figure()
    plt.plot(t,y_gauss, label="Aceleración suavizada")
    plt.plot(t[maximos], y_gauss[maximos], "x", label="Despegue", color="g")
    plt.plot(t[minimos], y_gauss[minimos], "x", label="Aterrizaje", color="r")
    plt.grid()
    plt.ylabel("Aceleración")
    plt.xlabel("Tiempo")
    plt.title("La aceleración de "+nombre+" es:")
    plt.legend()
    plt.show()
def graf_p():    
    plt.figure()
    plt.plot(t,P, label="Potencia")
    plt.plot(t[maximos], P[maximos], "x", label="Despegue", color="g")
    plt.plot(t[minimos], P[minimos], "x", label="Aterrizaje", color="r")
    plt.grid()
    plt.ylabel("Potencia")
    plt.xlabel("Tiempo")
    plt.title("La potencia de "+nombre+" es:")
    plt.legend()
    plt.show()
def graf_f():    
    plt.figure()
    plt.plot(t,F, label="Fuerza")
    plt.plot(t[maximos], F[maximos], "x", label="Despegue", color="g")
    plt.plot(t[minimos], F[minimos], "x", label="Aterrizaje", color="r")
    plt.title("La fuerza de "+nombre+" es:")
    plt.ylabel("Fuerza")
    plt.xlabel("Tiempo")
    plt.grid()
    plt.legend()
    plt.show()
def graf_v():    
    plt.figure()
    plt.plot(t,v, label="Velocidad")
    plt.plot(t[maximos], v[maximos], "x", label="Despegue", color="g")
    plt.plot(t[minimos], v[minimos], "x", label="Aterrizaje", color="r")
    plt.grid()
    plt.ylabel("Velocidad")
    plt.xlabel("Tiempo")
    plt.title("La velocidad de "+nombre+" es:")
    plt.legend()
    plt.show()
def graf_d():    
    plt.figure()
    plt.plot(t,d, label="Desplazamiento")
    plt.grid()
    plt.ylabel("Desplazamiento")
    plt.xlabel("Tiempo")
    plt.title("La desplazamiento de "+nombre+" es:")
    plt.legend()
    plt.show()
    

   

#------------------------------------------------------------------------------------

#VENTANA PRINCIPAL
def app_1():
    global app
    app = App(bg='#FFFFFF', title='ProMu', height=700, width=500)

    separa = Text(app, text=' ')
    separa.size = "24"
    logo = Picture(app, image="Logo Sin Fondo.png", width=300, height=300)

    separa = Text(app, text=' ')
    separa.size = "15"
    separa = Text(app, text=' ')
    separa.size = "15"
    boton_empezar = PushButton(app, text="EMPEZAR", command=empezar, width=20)
    boton_empezar.bg = "#C4C4C4"
    boton_empezar.font = "Eras Bold ITC"
    boton_empezar.text_size = "16"
    separa = Text(app, text=' ')
    separa.size = "15"
    boton_opciones = PushButton(app, text="MÁS INFORMACIÓN", command=opciones, width=20)
    boton_opciones.bg = "#C4C4C4"
    boton_opciones.font = "Eras Bold ITC"
    boton_opciones.text_size = "16"
    
    separa = Text(app, text=' ')
    separa.size = "15"
    boton_creditos = PushButton(app, text="CRÉDITOS", command=creditos, width=20)
    boton_creditos.bg = "#C4C4C4"
    boton_creditos.font = "Eras Bold ITC"
    boton_creditos.text_size = "16"

    app.display()

#VOLVER OPCIONES
def volver_opciones():
    opciones_window.hide()
    app.show()

#VOLVER CRÉDITOS
def volver_creditos():
    creditos_window.hide()
    app.show()

#SELECCIONAR ARCHIVO
def seleccionar_archivo():
    global archivo
    archivo = app.select_file(filetypes=[["Archivos Excel", "*.xlsx"]])
    if archivo:
        global nombre_archivo
        nombre_archivo = os.path.basename(archivo)
        text_excel = Text(añadir_salto_window, text="Has seleccionado:" + nombre_archivo)
        text_excel.font = "OCR A Extended"
        text_excel.size = "12"
        boton_enviar.enable()
        
def temporal():
    print("Botón Pulsado")
    
def volver_añadir_salto():
    añadir_salto_window.hide()
    saltos_window.show()
    
#VENTANA AÑADIR SALTO
def añadir_salto():
    saltos_window.hide()
    global añadir_salto_window
    añadir_salto_window = Window(saltos_window, title="Añadir Saltos", width=500, height=650)
    
    separa = Text(añadir_salto_window, text=' ')
    separa.size = "20"
    boton_volver = PushButton(añadir_salto_window, text="Volver Al Menú", command=volver_añadir_salto, width=15)
    boton_volver.bg = "#C4C4C4"
    boton_volver.font = "Eras Bold ITC"
    boton_volver.text_size = "12"
    
    separa = Text(añadir_salto_window, text=' ')
    separa.size = "20"
    boton_seleccionar = PushButton(añadir_salto_window, text="Seleccionar Archivo", command=seleccionar_archivo, width=25)
    boton_seleccionar.bg = "#C4C4C4"
    boton_seleccionar.font = "Eras Bold ITC"
    boton_seleccionar.text_size = "16"
    
    separa = Text(añadir_salto_window, text=' ')
    separa.size = "20"
    text_saltador = Text(añadir_salto_window, text="Nombre del Saltador:")
    text_saltador.font = "OCR A Extended"
    text_saltador.size = "12"
    global textbox_saltador
    textbox_saltador = TextBox(añadir_salto_window, width=50)
    textbox_saltador.bg = "#C4C4C4"
    
    separa = Text(añadir_salto_window, text=' ')
    separa.size = "15"
    text_masa = Text(añadir_salto_window, text="Masa:")
    text_masa.font = "OCR A Extended"
    text_masa.size = "12"
    global textbox_masa
    textbox_masa = TextBox(añadir_salto_window, width=50)
    textbox_masa.bg = "#C4C4C4"
    
    separa = Text(añadir_salto_window, text=' ')
    separa.size = "15"
    text_grupo = Text(añadir_salto_window, text="Grupo:")
    text_grupo.font = "OCR A Extended"
    text_grupo.size = "12"
    global textbox_grupo
    textbox_grupo = TextBox(añadir_salto_window, width=50)
    textbox_grupo.bg = "#C4C4C4"
    
    separa = Text(añadir_salto_window, text=' ')
    separa.size = "15"
    text_fecha = Text(añadir_salto_window, text="Fecha:")
    text_fecha.font = "OCR A Extended"
    text_fecha.size = "12"
    global textbox_fecha
    textbox_fecha = TextBox(añadir_salto_window, width=50)
    textbox_fecha.bg = "#C4C4C4"
    
    separa = Text(añadir_salto_window, text=' ')
    separa.size = "20"
    global boton_enviar
    boton_enviar = PushButton(añadir_salto_window, text="Enviar Datos", command= enviar_datos, width=20)
    boton_enviar.bg = "#C4C4C4"
    boton_enviar.font = "Eras Bold ITC"
    boton_enviar.text_size = "16"
    boton_enviar.disable()
    
def enviar_datos():
    t , a, av =sacar_datos(nombre_archivo)
    global H, Pmax , v, a_gauus, F, nombre
    H, Pmax, v, a_gauus, F = calcular_parametros( t, a, av, float(textbox_masa.value) )
    nombre = textbox_saltador.value
    grupo = textbox_grupo.value
    fecha = textbox_fecha.value
    global mensaje_recibido
    mensaje_recibido = enviar_data(nombre, grupo, int(H*10), fecha)
    boton_3.enable()
    text_bien = Text(añadir_salto_window, text="Datos Enviados Correctamente")
    text_bien.font = "OCR A Extended"
    text_bien.size = "12"

#VENTANA DE SALTOS
def saltos():
    global saltos_window
    saltos_window = Window(app, title="Saltos", width=500, height=400)
    Text(saltos_window, text="HAS INICIADO SESIÓN COMO: "+textbox_usuario.value, size=14, font="Eras Bold ITC")
    separa = Text(saltos_window, text=' ')
    separa.size = "40"
    
    box_1 = Box(saltos_window, layout="grid")

    boton_1 = PushButton(box_1, text="Añadir Salto", grid=[0, 0], command=añadir_salto, width=10)
    boton_1.bg = "#C4C4C4"
    boton_1.font = "Eras Bold ITC"
    boton_1.text_size = "16"

    box_2_3 = Box(saltos_window, layout="grid")

    boton_2 = PushButton(box_2_3, text="Mejores saltos", grid=[0, 0], command=ver_ranking, width=10)
    boton_2.bg = "#C4C4C4"
    boton_2.font = "Eras Bold ITC"
    boton_2.text_size = "16"

    global boton_3
    boton_3 = PushButton(box_2_3, text="Mi salto", grid=[1, 0], command= mi_salto, width=10)
    boton_3.bg = "#C4C4C4"
    boton_3.font = "Eras Bold ITC"
    boton_3.text_size = "16"
    boton_3.disable()

    box_4 = Box(saltos_window, layout="grid")

    boton_4 = PushButton(box_4, text="Salir", grid=[0, 0], command=salir, width=10)
    boton_4.bg = "#C4C4C4"
    boton_4.font = "Eras Bold ITC"
    boton_4.text_size = "16"

#FUNCION VOLVER MI SALTO
def volver_mi_salto():
    mi_salto_window.hide()
    saltos_window.show()
    
#VENTANA MI SALTO
def mi_salto():
    saltos_window.hide()
    global mi_salto_window
    mi_salto_window = Window(saltos_window, title="Mi Salto", width=750, height=750)
    separa = Text(mi_salto_window, text=' ')
    separa.size = "20"
    boton_volver = PushButton(mi_salto_window, text="Volver Al Menú", command=volver_mi_salto, width=15)
    boton_volver.bg = "#C4C4C4"
    boton_volver.font = "Eras Bold ITC"
    boton_volver.text_size = "12"
    separa = Text(mi_salto_window, text=' ')
    separa.size = "20"
    
    tusalto = Text(mi_salto_window, text='Tu salto ha sido de {0:.2f} centímetros'.format(H), font="OCR A Extended", size=15)
    tusalto_pmax = Text(mi_salto_window, text='La potencia máxima ha sido de {0:.2f} Newtons'.format(Pmax), font="OCR A Extended", size=15)
    tusalto_vmax = Text(mi_salto_window, text='La velocidad máxima ha sido de {0:.2f} m/s'.format(v0), font="OCR A Extended", size=15)
    tusalto_Fmax = Text(mi_salto_window, text='La fuerza maxima salto ha sido de {0:.2f} N'.format(Fmax), font="OCR A Extended", size=15)
    separa = Text(mi_salto_window, text=' ')
    separa.size = "20"
    
    borde_box1 = Box(mi_salto_window, width="1", height="1", border=True)
    grid = Box(borde_box1, layout="grid")
    
    t00 = Text(grid, text='LEAP MASTER LEGEND', font="OCR A Extended", size=20, color='#ff9700', align='left', grid=[0, 0])
    t10 = Text(grid, text='60/70 CM', font="OCR A Extended", size=20, color='#ff9700', align='right', grid=[1, 0])
    t01 = Text(grid, text='LEAP MASTER PRO', font="OCR A Extended", size=20, color='#ced500', align='left', grid=[0, 1])
    t11 = Text(grid, text='50/60 CM', font="OCR A Extended", size=20, color='#ced500', align='right', grid=[1, 1])
    t02 = Text(grid, text='LEAP MASTER ADVANCED', font="OCR A Extended", size=20, color='#00e42d', align='left', grid=[0, 2])
    t12 = Text(grid, text='40/50 CM', font="OCR A Extended", size=20, color='#00e42d', align='right', grid=[1, 2])
    t03 = Text(grid, text='LEAP MASTER MEDIUM', font="OCR A Extended", size=20, color='#12e0a8', align='left', grid=[0, 3])
    t13 = Text(grid, text='30/40 CM', font="OCR A Extended", size=20, color='#12e0a8', align='right', grid=[1, 3])
    t04 = Text(grid, text='LEAP MASTER DECENT', font="OCR A Extended", size=20, color='#0b109d', align='left', grid=[0, 4])
    t14 = Text(grid, text='20/30 CM', font="OCR A Extended", size=20, color='#0b109d', align='right', grid=[1, 4])
    t05 = Text(grid, text='LEAP MASTER CROOK', font="OCR A Extended", size=20, color='#610f02', align='left', grid=[0, 5])
    t15 = Text(grid, text='10/20 CM', font="OCR A Extended", size=20, color='#610f02', align='right', grid=[1, 5])
    separa = Text(mi_salto_window, text=' ')
    separa.size = "20"
    
    if H<20:
        t05.bg='#e5cfb4'
        t15.bg='#e5cfb4'
        enhorabuena = Text(mi_salto_window, text='¡Sigue Prácticando! Eres un LEAP MASTER CROOK', font="OCR A Extended", size=15)
    elif H>=20 and H<30:
        t04.bg='#bdd2ff'
        t14.bg='#bdd2ff'
        enhorabuena = Text(mi_salto_window, text='¡Nada Mal! Eres un LEAP MASTER DECENT', font="OCR A Extended", size=15)
    elif H>=30 and H<40:
        t03.bg='#d9fffa'
        t13.bg='#d9fffa'
        enhorabuena = Text(mi_salto_window, text='¡Muy Bien! Eres un LEAP MASTER MEDIUM', font="OCR A Extended", size=15)
    elif H>=40 and H<50:
        t02.bg='#bfff98'
        t12.bg='#bfff98'
        enhorabuena = Text(mi_salto_window, text='¡Enhorabuena! Eres un LEAP MASTER ADVANCED', font="OCR A Extended", size=15)
    elif H>=50 and H<60:
        t01.bg='#fdff98'
        t11.bg='#fdff98'
        enhorabuena = Text(mi_salto_window, text='¡Increíble! Eres un LEAP MASTER PRO', font="OCR A Extended", size=15)
    elif H>=60 :
        t00.bg='#ffe7ac'
        t10.bg='#ffe7ac'
        enhorabuena = Text(mi_salto_window, text='¡Qué Barbaridad! Eres un LEAP MASTER LEGEND', font="OCR A Extended", size=15)
    
    separa = Text(mi_salto_window, text=' ')
    separa.size = "20"
    boton_grafica1 = PushButton(mi_salto_window, text="Gráficos Disponibles", command=graficos, width=24)
    boton_grafica1.bg = "#C4C4C4"
    boton_grafica1.font = "Eras Bold ITC"
    boton_grafica1.text_size = "18"
    
def volver_graficos():
    graficos_window.hide()
    mi_salto_window.show()

def graficos():
    mi_salto_window.hide()
    global graficos_window
    graficos_window = Window(mi_salto_window, title="Gráficas", width=500, height=600)
    separa = Text(graficos_window, text=' ')
    separa.size = "20"
    boton_volver = PushButton(graficos_window, text="Volver Al Menú", command=volver_graficos, width=15)
    boton_volver.bg = "#C4C4C4"
    boton_volver.font = "Eras Bold ITC"
    boton_volver.text_size = "12"
    
    separa = Text(graficos_window, text=' ')
    separa.size = "20"
    boton_grafica1 = PushButton(graficos_window, text="Gráfico Aceleración", command= graf_a, width=24)
    boton_grafica1.bg = "#C4C4C4"
    boton_grafica1.font = "Eras Bold ITC"
    boton_grafica1.text_size = "18"
    
    separa = Text(graficos_window, text=' ')
    separa.size = "10"
    boton_grafica2 = PushButton(graficos_window, text="Gráfico Velocidad", command= graf_v, width=24)
    boton_grafica2.bg = "#C4C4C4"
    boton_grafica2.font = "Eras Bold ITC"
    boton_grafica2.text_size = "18"
    
    separa = Text(graficos_window, text=' ')
    separa.size = "10"
    boton_grafica3 = PushButton(graficos_window, text="Gráfico Desplazamiento", command= graf_d, width=24)
    boton_grafica3.bg = "#C4C4C4"
    boton_grafica3.font = "Eras Bold ITC"
    boton_grafica3.text_size = "18"

    separa = Text(graficos_window, text=' ')
    separa.size = "10"
    boton_grafica4 = PushButton(graficos_window, text="Gráfico Potencia", command= graf_p, width=24)
    boton_grafica4.bg = "#C4C4C4"
    boton_grafica4.font = "Eras Bold ITC"
    boton_grafica4.text_size = "18"
    
    separa = Text(graficos_window, text=' ')
    separa.size = "10"
    boton_grafica5 = PushButton(graficos_window, text="Gráfica Fuerza", command= graf_f, width=24)
    boton_grafica5.bg = "#C4C4C4"
    boton_grafica5.font = "Eras Bold ITC"
    boton_grafica5.text_size = "18"
    
def volver_leaderboard():
    ranking_window.hide()
    saltos_window.show()
    
#FUNCION PARA VER EL LEADERBOARD
def ver_ranking():
    saltos_window.hide()
    global ranking_window
    ranking_window = Window(app, title="Ranking", width=500, height=400)
    separa = Text(ranking_window, text=' ')
    separa.size = "20"
    boton_volver = PushButton(ranking_window, text="Volver Al Menú", command=volver_leaderboard, width=15)
    boton_volver.bg = "#C4C4C4"
    boton_volver.font = "Eras Bold ITC"
    boton_volver.text_size = "12"
    separa = Text(ranking_window, text=' ')
    separa.size = "10"
    ranking= enviar_getleaderboard()
    Text(ranking_window, text=ranking, size=12, font="OCR A Extended")

#FUNCIÓN DE INICIAR SESIÓN
def iniciar_sesion():
    if enviar_user(textbox_usuario.value):
        button_usuario.disable()
        text_correct = Text(empezar_window, text="Usuario correcto")
        text_correct.font = "OCR A Extended"
        text_correct.size = "12"
        separa = Text(empezar_window, text=' ')
        separa.size = "30"
        poner_contraseña()
    else:
        empezar_window.info('Error','Usuario incorrecto')
        
def iniciar_sesion2():
    if enviar_pass(textbox_contraseña.value):
        empezar_window.hide()
        saltos()
    else:
        empezar_window.info('Error','Contraseña incorrecta')
        
def poner_contraseña():
    text_contraseña = Text(empezar_window, text="Contraseña:")
    text_contraseña.font = "OCR A Extended"
    text_contraseña.size = "12"
    global textbox_contraseña
    textbox_contraseña = TextBox(empezar_window, width=50)
    textbox_contraseña.bg = "#C4C4C4"
    
    separa = Text(empezar_window, text=' ')
    separa.size = "15"
    button_contra = PushButton(empezar_window, text="COMPROBAR CONTRASEÑA", command=iniciar_sesion2, width=24)
    button_contra.bg = "#C4C4C4"
    button_contra.font = "Eras Bold ITC"
    button_contra.text_size = "14"
    
def volver_empezar():
    empezar_window.hide()
    app.show()

#VENTANA EMPEZAR
def empezar():
    app.hide()
    enviar_hello()
    global empezar_window
    empezar_window = Window(app, title="Menú", width=400, height=600)
    separa = Text(empezar_window, text=' ')
    separa.size = "15"
    boton_volver = PushButton(empezar_window, text="Volver Al Menú", command=volver_empezar, width=15)
    boton_volver.bg = "#C4C4C4"
    boton_volver.font = "Eras Bold ITC"
    boton_volver.text_size = "12"
    separa = Text(empezar_window, text=' ')
    separa.size = "15"
    Text(empezar_window, text="INTRODUCE TUS DATOS", size=16, font="Segoe UI Black")
    Text(empezar_window, text="PARA INICIAR SESIÓN", size=16, font="Segoe UI Black")
    separa = Text(empezar_window, text=' ')
    separa.size = "15"
    
    text_usuario = Text(empezar_window, text="Nombre de Usuario:")
    text_usuario.font = "OCR A Extended"
    text_usuario.size = "12"
    global textbox_usuario
    textbox_usuario = TextBox(empezar_window, width=50)
    textbox_usuario.bg = "#C4C4C4"
    
    separa = Text(empezar_window, text=' ')
    separa.size = "15"
    global button_usuario
    button_usuario = PushButton(empezar_window, text="COMPROBAR USUARIO", command=iniciar_sesion, width=24)
    button_usuario.bg = "#C4C4C4"
    button_usuario.font = "Eras Bold ITC"
    button_usuario.text_size = "14"
    
#Definimos webs
def open_webpage():
    webbrowser.open("https://leapmasterdeluxe.my.canva.site")
def open_webpage2():
    webbrowser.open('https://www.youtube.com/watch?v=vNurkAaDcJs')

#VENTANA OPCIONES
def opciones():
    app.hide()
    global opciones_window
    opciones_window = Window(app, title="Información", width=400, height=500)
    separa = Text(opciones_window, text=' ')
    separa.size = "15"
    
    Text(opciones_window, text="¡Ya disponible la página web", size=12, font="Segoe UI Black")
    Text(opciones_window, text="oficial de LEAP MASTER DELUXE!: ", size=12, font="Segoe UI Black")
    separa = Text(opciones_window, text=' ')
    separa.size = "15"
    boton_web = PushButton(opciones_window, text="Visitar Página", command=open_webpage, width=15)
    boton_web.bg = "#C4C4C4"
    boton_web.font = "Eras Bold ITC"
    boton_web.text_size = "12"
    
    separa = Text(opciones_window, text=' ')
    separa.size = "15"
    Text(opciones_window, text="¡Disponible también", size=12, font="Segoe UI Black")
    Text(opciones_window, text="el video guía!: ", size=12, font="Segoe UI Black")
    separa = Text(opciones_window, text=' ')
    separa.size = "15"
    boton_web = PushButton(opciones_window, text="Visitar Video", command=open_webpage2, width=15)
    boton_web.bg = "#C4C4C4"
    boton_web.font = "Eras Bold ITC"
    boton_web.text_size = "12"
    
    separa = Text(opciones_window, text=' ')
    separa.size = "15"
    boton_volver = PushButton(opciones_window, text="VOLVER AL MENÚ", command=volver_opciones, width=20)
    boton_volver.bg = "#C4C4C4"
    boton_volver.font = "Eras Bold ITC"
    boton_volver.text_size = "16"

#VENTANA CRÉDITOS
def creditos():
    app.hide()
    global creditos_window
    creditos_window = Window(app, title="Créditos", width=400, height=400)
    separa = Text(creditos_window, text=' ')
    separa.size = "15"
    Text(creditos_window, text="Miquel Navalón Moñinos", size=12, font="Segoe UI Black")
    Text(creditos_window, text="Nestor Espí Sánchez", size=12, font="Segoe UI Black")
    Text(creditos_window, text="Victor Mellado Luz", size=12, font="Segoe UI Black")
    Text(creditos_window, text="Nicolas de la Peña García", size=12, font="Segoe UI Black")
    Text(creditos_window, text="David Valls Lozano", size=12, font="Segoe UI Black")
    separa = Text(creditos_window, text=' ')
    separa.size = "15"
    boton_volver = PushButton(creditos_window, text="VOLVER AL MENÚ", command=volver_creditos, width=20)
    boton_volver.bg = "#C4C4C4"
    boton_volver.font = "Eras Bold ITC"
    boton_volver.text_size = "16"
    
def salir():
    enviar_quit()
    app.destroy()

if __name__=='__main__':
    app_1()
