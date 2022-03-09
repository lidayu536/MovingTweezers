#%%
import numpy as np



def f(buffer, sample_rate):
    x=-2
    y=3
    v=(y-x)/6e7
    D=1e-5*600*2*np.pi/(4e-3*8.5e-7)
    wc=1e8
    A=np.zeros(buffer)
    i=0
    # while i<2e7:
    #     A[i]=(wc*i/1e8)+D*x*i/1e8
    #     i=i+1
    while i<buffer:
        A[i]=np.mod(A[i-1]+(D*(x+v*i)+wc)/1e8,np.pi*2)
        i+=1
    # while i<1e8:
    #     A[i]=(wc*i/1e8)+D*y*i/1e8
    #     i=i+1
    return np.cos(A)
# %%
