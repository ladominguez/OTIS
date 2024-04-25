import numpy as np
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import glob
from otis import core
from otis.plotting.tools import get_spectrum_from_results, get_periods_from_results, get_average_spectrum
from matplotlib.pyplot import cm

component = 'HHZ'
#spectrum_files = glob.glob(os.path.join('spectra', '*ig','spectrum*' + component + '*.pkl'))
spectrum_files = glob.glob(os.path.join('spectra', '[n-z]*ig',f'spectrum*{component}_*.pkl'))
spectrum_files.sort()


if __name__ == '__main__':

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(6, 8))
    color = iter(cm.jet(np.linspace(0, 1, len(spectrum_files))))
    print('N: ', len(spectrum_files))
    color = iter(['salmon', 'maroon', 'navy', 'crimson', 'deeppink', 'purple', 'black', 'gold', 'red'])

    for file in spectrum_files:
        print(file)
        c = next(color)
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
        ax[0].plot(periods_at_touchdown, spectrum_at_touchdown, c=c, label=station, linewidth=1.5)
        ax[0].plot(periods_at_touchdown, average_spectrum, c=c, linestyle='--', linewidth=1.5)

        relative_spectrum = (10**spectrum_at_touchdown-10**average_spectrum) / 10**average_spectrum
        ax[1].plot(periods_at_touchdown, relative_spectrum, c=c, label=station, linewidth=1.5)
        ax[1].fill_between(periods_at_touchdown, relative_spectrum, 0, color=c, alpha=0.2)

    #ax.set_xscale('log')
    #ax.set_yscale('log')
    ax[0].set_xlabel('Period (s)')
    ax[0].set_ylabel('Amplitude')
    ax[0].set_xlim([2, 10])
    ax[0].set_ylim([2, 10])
    ax[0].set_title(f'Spectrum at touchdown - {component}')
    ax[0].grid('minor')
    ax[0].legend()
    ax[1].set_xlabel('Period (s)')
    ax[1].set_ylabel('Relative amplitude (x times)')
    ax[1].grid('both', linestyle='--')
    ax[1].axhline(0, color='black', linestyle='--')
    ax[1].set_xlim([2, 10])
    #ax[1].set_ylim([-50, 50])
    fig.savefig(f'spectrum_at_touchdown_{component}_2.png')
    print(f'Saved spectrum_at_touchdown_{component}_2.png')
    fig.show()

    
        
