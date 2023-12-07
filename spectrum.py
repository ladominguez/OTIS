import numpy as np
from obspy.core import read
from matplotlib import pyplot as plt
from mtspec import mtspec
from tqdm import tqdm
from utils import downsample_array

npts = 2**16
input_file = 'data/caig/caig.HHZ.sac'
T_min = 0.5
T_max = 10
overlap = 1.0

def main():

    sac = read(input_file)
    delta = round(sac[0].stats.delta * 100) / 100
    span_sec = sac[0].stats.endtime - sac[0].stats.starttime

    win = delta * (npts - 1)
    trim = sac.copy()
    trim.trim(starttime=sac[0].stats.starttime, endtime=sac[0].stats.starttime + span_sec)

    Aspec = np.array([])
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    j = 0

    for k, window in tqdm(enumerate(trim[0].slide(window_length=win, step=win*overlap)),
                          total=int(np.round(span_sec * 2 / win))):
        data = window.data
        if window.stats.npts > npts:
            data = data[:npts]

        if not k:
            spec, freq, jackknife, _, _ = mtspec(data=data, delta=delta, time_bandwidth=3.5,
                                            number_of_tapers=5, nfft=npts, statistics=True)
        else:
            spec, freq, jackknife, _, _ = mtspec(data=data, delta=delta, time_bandwidth=3.5,
                                            number_of_tapers=5, nfft=npts, statistics=True)
            
        freq = np.delete(freq, 0)
        spec = np.delete(spec, 0)
        T    = 1/freq
        ind = np.where((T >= T_min) & (T <= T_max))[0]

        #freq_down = downsample_array(freq,len(freq)//100)
        #spec_down = downsample_array(spec,len(freq)//100)
        T_down = T[ind]
        freq_down = freq[ind]
        spec_down = spec[ind]

        if k:
            Aspec = np.vstack([Aspec, np.log10(spec_down)])
        else:
            Aspec = np.log10(spec_down)

    
    

    np.savetxt('freq.txt', freq_down, fmt='%8.3f')
    np.savetxt('T.txt', T_down, fmt='%8.3f')
    np.savetxt('Aspec20.txt', Aspec, fmt='%8.3f')
    np.savetxt('spec.txt', spec_down, fmt='%8.3f')
    #ax.grid(True, which='both')
    #fig.savefig('fig.png')

if __name__ == "__main__":
    main()

