import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from numpy import cos, sin, pi, absolute, arange, array, append, abs, angle,\
                  fft, linspace, zeros, log10, unwrap
from scipy.signal  import kaiserord, lfilter, firwin, freqz, butter, lfilter
from pylab import figure, clf, plot, xlabel, ylabel, xlim, ylim, title, grid, \
                  axes, show, subplot, axis, plot

#function for sinusoidal generation
# def sine_generator(fs, sinefreq, duration):
#     T = duration
#     nsamples = fs * T*10
#     w = 2. * np.pi * sinefreq
#     t_sine = np.linspace(0, T, nsamples, endpoint=False)
#     y_sine = np.sin(w * t_sine)
#     result = pd.DataFrame({ 
#         'data' : y_sine} ,index=t_sine)
#     return result

# #function butter_bandpass
# def butter_bandpass(lowcut, highcut, fs, order=3):
#     nyq = 0.5 * fs
#     low = lowcut / nyq
#     high = highcut / nyq
#     b, a = butter(order, [low, high], btype='band')
#     return b, a

# #function butter_bandpass_filter
# def bp_filter(data, lowcut, highcut, fs, order=3):
#     b, a = butter_bandpass(lowcut, highcut, fs, order=order)
#     y = lfilter(b, a, data)
    
#     return y


import numpy as np
from scipy.fft import fft, ifft

# Define nextpow2 function
def nextpow2(N):
    """ Function for finding the next power of 2 """
    n = 1
    i = 0
    while n < N: 
        n *= 2
        i += 1
    return i

def bp_filter(d, dt, f1, f2, f3, f4):
    # Assuming d, f1, f2, f3, f4, and dt are already defined
    # nt, nx = d.shape
    if d.ndim == 1:
        nt = d.shape[0]
    else:
        nt, nx = d.shape

    k = nextpow2(nt)
    nf = 4 * (2 ** k)

    i1 = int(np.floor(nf * f1 * dt))
    i2 = int(np.floor(nf * f2 * dt))
    i3 = int(np.floor(nf * f3 * dt))
    i4 = int(np.floor(nf * f4 * dt))

    up = np.linspace(0, 1, i2 - i1, endpoint=False)
    down = np.linspace(1, 0, i4 - i3, endpoint=False)
    aux = np.concatenate([np.zeros(i1), up, np.ones(i3 - i2), down, np.zeros(nf // 2 + 1 - i4)])
    aux2 = np.flip(aux[1:nf // 2])

    c = 0  # zero phase
    F = np.concatenate([aux, aux2])
    Phase = (np.pi / 180) * np.concatenate([[0], -c * np.ones(nf // 2 - 1), [0], c * np.ones(nf // 2 - 1)])
    Transfer = F * np.exp(-1j * Phase)

    D = fft(d, nf, axis=0)

    Do = np.zeros_like(D, dtype=complex)
    if d.ndim == 1:
        Do = Transfer * D
        o = ifft(Do, nf, axis=0)
        o = np.real(o[:nt])
    else:
        for k in range(nx):
            Do[:, k] = Transfer * D[:, k]
        
        o = ifft(Do, nf, axis=0)
        o = np.real(o[:nt, :])

    # o = ifft(Do, nf, axis=0)
    # o = np.real(o[:nt, :])
    
    return o
