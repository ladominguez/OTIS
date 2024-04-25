import numpy as np
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import glob
from otis import core
from otis.plotting.tools import get_spectrum_from_results, get_periods_from_results, get_average_spectrum, get_periods_from_results, get_index_from_period
from matplotlib.pyplot import cm
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FixedLocator

component = 'HHN'
T0 = 4 
#spectrum_files = glob.glob(os.path.join('spectra', '*ig','spectrum*' + component + '*.pkl'))
spectrum_files = glob.glob(os.path.join('spectra', '[n-z]?ig',f'spectrum*{component}_*.pkl'))
spectrum_files.sort()

if __name__ == '__main__':


    color = iter(cm.jet(np.linspace(0, 1, len(spectrum_files))))
    print('N: ', len(spectrum_files))
    color = iter(['salmon', 'maroon', 'navy', 'crimson', 'deeppink', 'purple', 'black', 'gold', 'red'])

    for k, file in enumerate(spectrum_files):
        print(file)
        c = next(color)
        results, config = core.read_spectrum2file(file)
        times = core.get_times_from_results(results)
        station = config['station']['name']
        component = config['station']['component']
        periods = get_periods_from_results(results)
        spectrum = get_spectrum_from_results(results)
        ind_T0 = get_index_from_period(results, T0)

        spectrum_at_T0 = spectrum[:,ind_T0]

        if k == 0:
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4), squeeze=True)
            ax.set_xlabel('Time')
            ax.set_ylabel('Amplitude')
            ax.set_title(f'Spectrum at {T0} s - {component}')
            ax.grid('minor')
            ax.set_xlim(min(times).datetime, max(times).datetime)

            xticks = ax.get_xticks()
            ax.xaxis.set_major_locator(FixedLocator(xticks))
            ax.set_xticklabels(xticks, rotation=45)

            date_form = DateFormatter("%Y-%b-%d")
            ax.xaxis.set_major_formatter(date_form)


        ax.plot(times, spectrum_at_T0, c=c, label=station, linewidth=1.5)
     
    t_touch = core.get_touchdown_time() 
    ax.axvline(t_touch, color='black', linestyle='--')
    ax.legend()

    fig.savefig(f'spectrum_at_period_{T0}s_{component}.png')
    print(f'Saved spectrum_at_period_{T0}a_{component}.png')
    fig.show()

    
        
