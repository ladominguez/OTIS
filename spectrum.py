#!/usr/bin/env python
# coding: utf-8

from obspy.core import read
from matplotlib import pyplot as plt
from mtspec import mtspec
import numpy as np
from tqdm import tqdm

npts     = np.power(2,10)

sac = read('caig.sac');
delta = np.round(sac[0].stats.delta*100)/100
span_sec = sac[0].stats.endtime - sac[0].stats.starttime

win = delta*(npts -1)
trim = sac.copy()
trim.trim(starttime=sac[0].stats.starttime, endtime=sac[0].stats.starttime+span_sec)


print(sac[0].stats.starttime)
print(sac[0].stats.endtime)
print("Delta: ", delta, ' s.')
print("npts: ",npts)
print("Win size: ", win, ' s.')
print("Span: ", span_sec, ' s.')


return
Aspec = {}
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

j=1

for k, window in tqdm(enumerate(trim[0].slide(window_length=win, step=win/2)),total=np.round(span_sec*2/win)):
    data = window.data
    #print('starttime: ',window.stats.starttime, ' endtime: ', window.stats.starttime, ' npts:', len(data))
    if window.stats.npts > npts:
        data=data[slice(npts)]
    
    spec, freq, jackknife, _, _ = mtspec(data=data, delta=delta, time_bandwidth=3.5, number_of_tapers=5, nfft=npts, statistics=True)
    freq = np.delete(freq,0)
    spec = np.delete(spec,0)
    Aspec[k]=spec
    ax.loglog(1/freq, Aspec[k])
    j=j+1


print("Total: ", j)    
ax.grid(True, which='both')    
fig.savefig('fig.png')




