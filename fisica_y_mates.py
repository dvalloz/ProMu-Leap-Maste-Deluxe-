import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
import numpy as np
from scipy.ndimage import gaussian_filter1d as gf

def primitivaNumerica(variable, tiempo, y0):
    return cumtrapz(variable,x=tiempo,initial=y0)

g=9.81
m=68
fichero="muestras.xlsx"
df=pd.read_excel(fichero)

t=df.values[:,0].astype(float)

a=df.values[:,1].astype(float)
ay=df.values[:,3].astype(float)

av=a*np.sign(ay)

a_g=a-g
av_g=av-g

#Aceleracion suavizada
y_gauss = gf(av_g, 5)

#Fuerza al dar el salto
F=av*m

#Velocidad
v=primitivaNumerica(av_g,t,0)
#Velocidad Maxima
v0=v.max()

sacudida = np.gradient(t, av_g)
snap_s = np.gradient(t, sacudida)
maximos = np.argmax(v)
minimos = np.argmin(v)


#Final del impulso
tfi= t[maximos]
#Final del vuelo
tfv= t[minimos]
#Duracion del tiempo de vuelo
T=tfv-tfi
print("Tiempo de vuelo: {0} segundos".format(T))

#Potencia
P=F*v
#Potencia máxima
Pmax=4800
#Potencia normalizada
Pn=Pmax/m
print("Potencia máxima normalizada: {0:.2f} W/kg".format(Pn))

#Altura del salto a partir de v0 (en cm)
H=v0**2/2*g
print("Altura del salto: {0:.2f} cm".format(H))
#Altura del salto a partir de T
H2=(g*T**2)/8
 


plt.plot(t,y_gauss, label="Aceleracion gauss")
plt.plot(t,v, label="Velocidad")
plt.grid()
plt.legend()
plt.show()

def graf_a():
    plt.plot(t,y_gauss, label="Aceleracion gauss")
    plt.grid()
    plt.legend()
    plt.show()
    
def graf_v():
    plt.plot(t,v, label="Velocidad")
    plt.grid()
    plt.legend()
    plt.show()

    

def sacar_datos(nombre_fichero):
    # Definir variable g como variable global
    fichero= nombre_fichero
    df=pd.read_excel(fichero)

    t=df.values[:,0].astype(float)

    a=df.values[:,1].astype(float)
    ay=df.values[:,3].astype(float)

    av=a*np.sign(ay)

    a_g=a-g
    av_g=av-g
    
    return t, av_g 

def calcular_parametros( t, av_g ):
    #Aceleracion suavizada
    y_gauss = gf(av_g, 5)

    #Fuerza al dar el salto
    F=av*m

    #Velocidad
    v=primitivaNumerica(av_g,t,0)
    #Velocidad Maxima
    v0=v.max()

    sacudida = np.gradient(t, av_g)
    snap_s = np.gradient(t, sacudida)
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
    
    return T, P, H

















