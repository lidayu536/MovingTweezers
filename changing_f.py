#%%
from pyspcm import *
from spcm_tools import *
import scipy.signal as signal
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import wave
from awg import*
from awg2 import*


def func(x,phi0,A):
    return A*np.cos(x+phi0)


def transfer( f, t ,N, phi0,A):
    phi=np.linspace(0,0,N)
    for i in range(N-1):
        phi[i+1]=phi[i]+f[i+1]*(t[i+1]-t[i])
    #phi[i] is the phace of t[i]
    y=func(phi,phi0,A)
    return y

'''
def tryit():
    N=100000
    T=1
    F=100
    t=np.linspace(0,T,N)
    f=np.linspace(0,F,N)
    for i in range(int(N/2)):
        f[i]=F/2
    #f:frequent. From t[0] to t[N/2], f doesn't change.  From t[N/2] to t[N], f change from F/2 to F
    transfer(f,t,N,0,1)

#tryit()
'''

def mkwv(y,fs):
    #transfer y to a .wav file
    wave_data = y.astype(np.short)
    f = wave.open(r"chgf.wav", "wb")
    f.setnchannels(1)
    f.setsampwidth(3)
    f.setframerate(fs)
    f.writeframes(wave_data.tostring())
    f.close()



def changef(n,F0,F1,N):
    #n is an integer ,and describes the number of simple_cosine_waves
    #F0 is an array, and describes the original frequencies of the n simple_cosine_waves
    #F1 is an array, and describes the target frequencies of the n simple_cosine_waves
    #N is the number of samples
    F=np.zeros((n,N))
    for i in range(n):
        f0 = np.linspace(F0[i],F1[i],int(N/2))
        f1 = np.linspace(F0[i],F0[i],int(N/4))
        f2 = np.linspace(F1[i],F1[i],int(N/4))
        f10 = np.append(f1,f0)
        f = np.append(f10,f2)
        F[i]= f
    return F
    #F is a 2-dimension array, and F[i] describes the changing process of the no.i simple_cosine_wave's frequency 

def ftowv(n,F,A,phi0,N):
    #n the same meaning in changef()
    #F the same meaning in changef()
    #N the same meaning in changef()
    #phi0 is an array, and describes the original phases of the n simple_cosine_waves
    T=1
    t=np.linspace(0,T,N)
    y=np.linspace(0,0,N)
    
    for i in range(n):
        y = y + transfer(F[i], t, N, phi0[i], A[i])
    
    #plt.plot(t,y)
    #plt.show()
    #mkwv(y,N/T)
   
    return y


def example1():
    n=int(3)
    F0=[100,300,400]
    F1=[200,300,400]
    A=[100000,100000,100000]
    phi0=[0,1,2]
    
    awg = AWG2()
    awg.open()
    awg.set_buffer_size(8192)
    awg.config()
    N=awg.llMemSamples.value
    F=changef(n,F0,F1,N)
    y1=ftowv(n,F,A,phi0,N)
    y2=ftowv(1,changef(1,[100],[200],N),[100000],[0], N)
    awg.arbitrary_synthesis(y1,y2,1000000)
    awg.close()
example1()

