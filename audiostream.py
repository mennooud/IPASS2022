#! /usr/bin/python

import numpy as np
import pyaudio
from scipy.signal import butter, lfilter
from scipy.fftpack import fft
import time

def bandpass(lowcut, highcut, fs, order):
    '''
    implementing Butterworth Bandpass
    https://scipy-cookbook.readthedocs.io/items/ButterworthBandpass.html?highlight=butterworth#butterworth-bandpass

    :param lowcut: Low cutoff frequency
    :param lowcut: High cutoff frequency
    :param fs: sampling rate
    :param cutoff: cutoff frequency
    '''
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# config
CHUNK = 1024 * 4
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# pyaudio class instance
# stream object to get data input
def start_stream():
    p = pyaudio.PyAudio()
    frames_per_buffer = CHUNK
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=True,
        frames_per_buffer=frames_per_buffer
    )

    print('stream started')
    result = np.array([], dtype=np.int16)

    while True:
        data = stream.read(frames_per_buffer)
        stream.write(data)

        newdata = np.frombuffer(data, dtype=np.int16)

'''
        x = np.fft.fft(newdata)  # numpy functie voor Fast Fourier Transform algoritme
        freqs = np.fft.fftfreq(len(x))  # return
        index = np.argmax(np.abs(x))  # index
        freq = freqs[index]
        hz = int(abs(freq * RATE))
        #print(newdata)

        if hz > 16 and hz < 60:  # Sub-bass	        20 to 60 Hz
            print('Sub-bass')

'''

    stream.stop_stream()
    stream.close()
    p.terminate()

start_stream()