# -*- coding: utf-8 -*-

import numpy as np
import csv
from scipy import stats,signal, integrate
import matplotlib.pyplot as plt
 

"""
(20 %) Crear un esquema de modulación BPSK para los bits presentados. Esto implica asignar una forma de onda sinusoidal normalizada (amplitud unitaria) para cada bit y luego una concatenación de todas estas formas de onda.
"""

#Se ingresan los bits a procesar en un array de numpy llamado bits:
with open("bits10k.csv", 'r') as bits:
    reader = csv.reader(bits, delimiter=',')
    bits = np.array(list(reader)).astype(float)
    
    
#Se averigua el número de bits por procesar, esta información se utilizará más adelante
N = len(bits)

#Frecuencia de operación para la onda portadora (requisito de la tarea)
f = 5000

#Duración del periodo de cada onda
T = 1/f

#Número de puntos de muestreo por periodo, se toman 50 para poder ver claramente la forma sinusoidal
p = 50

#Puntos de muestreo para cada periodo
tp = np.linspace(0,T,p)

#Creación de la forma de onda
sin = np.sin(2*np.pi*f*tp)

#Visualización de la forma de onda portadora
plt.plot(tp, np.sin(2*np.pi*f*tp))
plt.xlabel("Tiempo (ms)")
plt.show

#Frecuencia de muestreo
fs = p/T

#Creación de la línea temporal para toda la señal Tx
t = np.linspace(0,N*T,N*p) #Tiempo para que quepan todos los bits

#Vector de ceros para después encajar ahí la señal que modula los bits
senal = np.zeros(N*p)

#Creación de la señal modulada. Tenemos que recorrer todos los bits, y para cada bit asignar una forma de onda dentro de la señal.
for k,b in enumerate(bits): #(índice,bit)
    senal[k*p:(k+1)*p] = (2*b-1)*sin #(2*b-1) es para pasar los bits a -1 y 1, así los -1 representan 0 y los 1 representan 1
    
#Visualización de los primeros bits modulados    
pb = 3
plt.figure()
plt.plot(senal[0:pb*p])
plt.xlabel("Puntos de muestreo: 50 por cada periodo (un periodo = un bit modulado)")
plt.ylabel("Señal modulada")
plt.show

"""
2) Calcular la potencia promedio de la señal modulada generada.
"""
#Potencia instantánea
Pinst = senal**2

#Potencia promedio Promedio temporal de la potencia instantánea
Ps = integrate.trapz(Pinst,t) / (T*N)
print("Potencia promedio temporal de la señal: ",Ps)

"""
3) Simular un canal ruidoso del tipo AWGN (ruido aditivo blanco gaussiano) 
con una relación señal a ruido (SNR) desde -2 hasta 3 dB.
"""
resultados_ber = np.zeros(6)
for snr in [-2,-1,0,1,2,3]:
    
    # Relación señal-a-ruido deseada
    SNR = snr
    
    # Potencia del ruido para SNR y potencia de la señal dadas
    Pn = Ps / (10**(SNR / 10))
    
    # Desviación estándar del ruido
    sigma = np.sqrt(Pn)
    
    # Crear ruido (Pn = sigma^2)
    ruido = np.random.normal(0, sigma, senal.shape)
    
    #"El canal": señal recibida
    Rx = senal + ruido
    

    #Visualización de los primeros bits recibidos (ya con ruido)
    pb = 3
    plt.figure()
    plt.ylabel("Señal con ruido")
    plt.plot(Rx[0:pb*p])
    plt.title("Visualización de primeros 3 bits con ruido.")
    plt.show
    
    """
    4) Graficar la densidad espectral de potencia de la señal 
    con el método de Welch (SciPy), antes y después del canal ruidoso
    """
    
    
    fw, PSD = signal.welch(senal, fs, nperseg=1024) # Antes del canal ruidoso
    fr, PSD2 = signal.welch(Rx, fs, nperseg=1024) # Después del canal ruidoso
    plt.figure()
    plt.semilogy(fw, PSD, label="Antes del canal ruidoso")
    plt.semilogy(fr, PSD2,"r-", label="Después del canal ruidoso")
    plt.legend()
    plt.xlabel('Frecuencia / Hz')
    plt.ylabel('Densidad espectral de potencia / V**2/Hz')
    plt.show()
    
    
    """
    5) Demodular y decodificar la señal
    """
    #Energía de la señal: integral de la potencia
    Es = np.sum(sin**2)
    #Se espera energía alrededor de cero, o alrededor de 24.5
    
    #Inicialización del vector de bits recibidos:
    bitsRx = np.zeros(bits.shape)
    
    #Decodificación de la señal por detección de energía
    for k in range(len(bitsRx)):
        E = np.sum(Rx[k*p:(k+1)*p]*sin)  
        if E > 0: #E será positivo o negativo según se reciba sen o -sen, por lo que se compara con 0.
            bitsRx[k] = 1
        else: 
            bitsRx[k] = 0
            
    
    #Suma de los arrores
    err = np.sum(abs(bits - bitsRx))
    
    #Tasa de error de bits
    BER = err/N
    
    resultados_ber[snr+2] = BER
    print('Hay un total de {} errores en {} bits para una tasa de error de {}.Esto para un SNR = {}'.format(err, N, BER,snr))
    
    

"""
Gráfica especial para comparar tres SNR en la densidad espectral de potencia
"""

 # Relación señal-a-ruido deseada
SNR1 = -2
SNR2 = 3
SNR0 = 0
    
# Potencia del ruido para SNR y potencia de la señal dadas
Pn1 = Ps / (10**(SNR1 / 10))
Pn2 = Ps / (10**(SNR2 / 10))
Pn0 = Ps / (10**(SNR0 / 10))
    
# Desviación estándar del ruido
sigma1 = np.sqrt(Pn1)
sigma2 = np.sqrt(Pn2)
sigma0 = np.sqrt(Pn0)

# Crear ruido (Pn = sigma^2)
ruido1 = np.random.normal(0, sigma1, senal.shape)
ruido2 = np.random.normal(0, sigma2, senal.shape)
ruido0 = np.random.normal(0, sigma0, senal.shape)

#"El canal": señal recibida
Rx1 = senal + ruido1
Rx2 = senal + ruido2
Rx0 = senal + ruido0
    

fw, PSD = signal.welch(senal, fs, nperseg=1024) # Antes del canal ruidoso
fr, PSD2 = signal.welch(Rx1, fs, nperseg=1024) # Después del canal ruidoso
fr3, PSD3 = signal.welch(Rx2, fs, nperseg=1024)
fr0, PSD0 = signal.welch(Rx0, fs, nperseg=1024)
plt.figure()
plt.semilogy(fw, PSD, label="Antes del canal ruidoso")
plt.semilogy(fr, PSD2,"r-", label="Después del canal ruidoso con SNR = -2")
plt.semilogy(fr0, PSD0,"m-", label="Después del canal ruidoso con SNR = 0")

plt.semilogy(fr3, PSD3,"g-", label="Después del canal ruidoso con SNR = 3")
plt.legend()
plt.xlabel('Frecuencia / Hz')
plt.ylabel('Densidad espectral de potencia / V**2/Hz')
plt.show()
  
"""
6) Graficar BER versus SNR.
"""

plt.figure()
plt.plot([-2,-1,0,1,2,3],resultados_ber,color='m');
plt.plot([-2,-1,0,1,2,3],resultados_ber,"o", color='black');
plt.title('BER contra SNR')
plt.ylabel('BER (tasa de error de bits)')
plt.xlabel('SNR (relación señal a ruido)')
plt.show()


"""

Prueba extra para ver cuándo falla la decodificación

"""

resultados_ber = np.zeros(6)
for snr in [-8,-7,-6,-5,-4,-3]:
    
    # Relación señal-a-ruido deseada
    SNR = snr
    
    # Potencia del ruido para SNR y potencia de la señal dadas
    Pn = Ps / (10**(SNR / 10))
    
    # Desviación estándar del ruido
    sigma = np.sqrt(Pn)
    
    # Crear ruido (Pn = sigma^2)
    ruido = np.random.normal(0, sigma, senal.shape)
    
    #"El canal": señal recibida
    Rx = senal + ruido
  
    """
    Demodular y decodificar la señal para la prueba extra
    """
    #Energía de la señal: integral de la potencia
    Es = np.sum(sin**2)
    #Se espera energía alrededor de cero, o alrededor de 24.5
    
    #Inicialización del vector de bits recibidos:
    bitsRx = np.zeros(bits.shape)
    
    #Decodificación de la señal por detección de energía
    for k in range(len(bitsRx)):
        E = np.sum(Rx[k*p:(k+1)*p]*sin)  
        if E > 0: #E será positivo o negativo según se reciba sen o -sen, por lo que se compara con 0.
            bitsRx[k] = 1
        else: 
            bitsRx[k] = 0
            
    
    #Suma de los arrores
    err = np.sum(abs(bits - bitsRx))
    
    #Tasa de error de bits
    BER = err/N
    
    resultados_ber[snr+8] = BER
    print('Hay un total de {} errores en {} bits para una tasa de error de {}.Esto para un SNR = {}'.format(err, N, BER,snr))


"""
Gráfica extra de BER vs SNR
"""
plt.figure()
plt.plot([-8,-7,-6,-5,-4,-3],resultados_ber,color='m');
plt.plot([-8,-7,-6,-5,-4,-3],resultados_ber,"o", color='black');
plt.title('BER contra SNR')
plt.ylabel('BER (tasa de error de bits)')
plt.xlabel('SNR (relación señal a ruido)')
plt.show()