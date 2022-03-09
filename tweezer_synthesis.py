#%%
from scipy.fft import ifft
import numpy as np


def synthesis(buffer, sample_rate, f_array):
    l = np.zeros(buffer)
    f_index = np.round(f_array/sample_rate*buffer).astype(np.int)
    l[f_index] = 1.0
    l[buffer-f_index] = 1.0
    mask = 2.0*(np.abs(np.angle(ifft(l)))<np.pi/2)-1.0
    return np.abs(ifft(l))*mask

def normalize(arr):
    max = np.abs(np.max(arr)) if np.abs(np.max(arr))>np.abs(np.min(arr)) else np.abs(np.min(arr))
    return arr/max

def convert_to_int(arr):
    return np.round(32767*arr).astype(np.int16)

def convert_to_int2(arr):
    return np.round(32767*arr).astype(np.int32)

# %%
