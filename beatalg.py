#import matplotlib.pyplot as plt
from scipy.fftpack import fft, fft2, ifft
import math
from numpy import floor, zeros, power, real
import scipy.io.wavfile as wav
from scipy import misc, cos, pi
from os import path
from pydub import AudioSegment
import soundfile as sf
import wave

bandlimits = [0, 200, 400, 800, 1600, 3200]
maxfreq = 4096

fs,sig = wav.read("cink1.wav")
signal = wave.open("cink1.wav", "rb")
if(signal.getnchannels() == 2):
    sig = (sig[:,0] + sig[:,1])/2  #if stereo to mono
length = (sig.size)
sample_size = floor(2.2*2*maxfreq)
print(sample_size)
start = floor(length/2 - sample_size/2)
start = int(start)
print(start)
stop = floor(length/2 + sample_size/2)
stop = int(stop)
print(stop)

short_sample = sig[start:stop]
print(short_sample.size)

dft = fft(short_sample)
print(dft.shape)

n = len(dft)
nbands = len(bandlimits)

bl = []
br = []

for i in range(0, nbands-1): #rozsah upravit, zatial ponechat
    bl.append(int(floor(bandlimits[i]/maxfreq*n/2)+1))
    br.append(int(floor(bandlimits[i+1]/maxfreq*n/2)))
    print(br[i])

bl.insert(nbands-1, int(floor(bandlimits[nbands-1]/maxfreq*n/2)+1))
#br.insert(nbands-1, int(floor(n/2)))
br.append(int(floor(n/2)))
'''
for i in range(0, len(bl)):
    print(bl[i])

for i in range(0, len(br)):
    print(br[i])
'''
output = zeros((n,nbands),dtype=complex)

for a in range(0, nbands):
    output[bl[a]:br[a], a] = dft[bl[a]:br[a]]
    #print(output[bl[a]:br[a], a])
    output[n+1-br[a]:n+1-bl[a],a] = dft[n+1-br[a]:n+1-bl[a]]

output[0][0] = 0

#hwindow
winlength = 0.2 #edit
hannlen = winlength*2*maxfreq;
hannlen = int(hannlen)
print(hannlen)

print("n is ", n)

hann = zeros((n,1),dtype=complex)

for a in range(0, hannlen-1):
    val = (cos(a*pi/hannlen/2))
    hann[a] = power(val, 2)

print("Hannn ",len(hann[:,0]))

wave = zeros((n,nbands),dtype=complex)
for i in range(0, nbands):
    wave[:,i] = real(ifft(output[:,i]))

freq = zeros((n,nbands),dtype=complex)
for i in range(0, nbands-1):
    for j in range(0, n):
        if(wave[j,i] < 0):
            wave[j,i] = - wave[j,i]
    freq[:,i] = fft(wave[:,i])

filtered = zeros((n,nbands),dtype=complex)
output2 = zeros((n,nbands),dtype=complex)

for i in range(0, nbands-1):
    filtered[:,i] = freq[:,i]*fft(hann[:,0])
    output2[:,i] = real(ifft(filtered[:,i]))

#diffrect

n = len(output2)
sig = output2

output3 = zeros((n,nbands),dtype=complex)

for i in range(0, nbands-1):
    for j in range(4, n-1):
        d = sig[j,i] - sig[j-1,i]

        if d > 0:
            output3[j,i] = d

#combfilter

sig = output3

n = len(sig)

npulses = 3;

dft = zeros((n,nbands),dtype=complex)

for i in range(0, nbands-1):
    dft[:,i] = fft(sig[:,i])

maxe = 0
minbpm =  60
maxbpm =  240
sbpm = 1
for bpm in range(minbpm,maxbpm,2):

    e = 0

    fil = zeros((n,1), float)

    nstep = floor(120/bpm*maxfreq)
    nstep = int(nstep)

    for a in range(0, npulses-1):
        fil[a*nstep+1] = 1

    dftfil = fft(fil)


    for i in range(0, nbands-1):
        val = (abs(dftfil[:,0]*dft[:,i]))
        x = power(val, 2)
        e = e + sum(x)

        #print(maxe)
    if e > maxe:
        sbpm = bpm*0.9#scaling edit
        maxe = e

output4 = sbpm
print(output4)
