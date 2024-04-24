import numpy as np
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import glob
from otis import core
from otis.plotting.tools import get_spectrum_from_results, get_periods_from_results, get_average_spectrum

component = 'HHE'
spectrum_files = glob.glob(os.path.join('spectra', '*ig','spectrum*' + component + '*.pkl'))

if __name__ == '__main__':

    fig, ax = plt.subplots(figsize=(6, 8))
    for file in spectrum_files:
        print(file)
        results, config = core.read_spectrum2file(file)
        times = core.get_times_from_results(results)
        station = config['station']['name']
        component = config['station']['component']
        t_touchdown = core.get_touchdown_UTCDatetime()
        t_touchdown_index = core.get_index_from_time(results, t_touchdown)
        periods = get_periods_from_results(results)
        spectrum = get_spectrum_from_results(results)
        spectrum_at_touchdown = spectrum[t_touchdown_index,:]
        periods_at_touchdown = periods[t_touchdown_index,:]
        average_spectrum = get_average_spectrum(results, 20, 240)
        ax.plot(periods_at_touchdown, spectrum_at_touchdown, label=station)
        ax.plot(periods_at_touchdown, average_spectrum, label=station + ' average', linestyle='--')

    ax.set_xscale('log')
    #ax.set_yscale('log')
    ax.set_xlabel('Period (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Spectrum at touchdown')
    ax.grid('minor')
    ax.legend()
    fig.show()

    
        
