import numpy as np
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import glob
from otis import core
from otis.plotting.tools import get_spectrum_from_results, get_periods_from_results, get_average_spectrum, get_periods_from_results, get_index_from_period 
from otis.plotting.plot import plot_hurracaine_stages
from matplotlib.pyplot import cm
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FixedLocator
from datetime import datetime
from matplotlib.ticker import FormatStrFormatter
from geopy.distance import great_circle
from ssn import get_station_by_name

component = 'HHZ'
T0 = 4 
#suffix='2'
stations = [  'CAIG', 'MEIG', 'PLIG', 'PZIG']
for k, station in enumerate(stations):
    if k == 0:
        spectrum_files  = glob.glob(os.path.join('spectra', station.lower(),'spectrum*' + component + '*.pkl'))
    else:
        spectrum_files += glob.glob(os.path.join('spectra', station.lower(),'spectrum*' + component + '*.pkl'))
#spectrum_files = glob.glob(os.path.join('spectra', '[a-m]?ig',f'spectrum*{component}_*.pkl'))
#spectrum_files = glob.glob(os.path.join('spectra', '[n-z]?ig',f'spectrum*{component}_*.pkl'))
spectrum_files.sort()

if __name__ == '__main__':


    color = iter(cm.jet(np.linspace(0, 1, len(spectrum_files))))
    #print('N: ', len(spectrum_files))
    color = iter(['black','red', 'maroon', 'navy', 'salmon', 'deeppink', 'purple', 'black', 'gold', 'crimson'])

    output_dir = os.path.join('figures', f'spectrum_at_period_{T0}s')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for k, file in enumerate(spectrum_files):
        print(file)
        c = next(color)
        #c = 'black'
        results, config = core.read_spectrum2file(file)
        times = core.get_times_from_results(results)
        station = config['station']['name']
        component = config['station']['component']
        periods = get_periods_from_results(results)
        spectrum = get_spectrum_from_results(results)
        spectrum = np.array([np.clip(result[1], -15, None) for result in results])
        ind_T0 = get_index_from_period(results, T0)

        spectrum_at_T0 = spectrum[:,ind_T0]

        lat_touchdown, lon_touchdown = core.get_touchdown_coordinates()
        stla, stlo = get_station_by_name(station)
        distance_to_touchdown = great_circle((stla, stlo), (lat_touchdown, lon_touchdown)).kilometers

        if k == 0:
        #if True:
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 6), squeeze=True)
            ax.set_xlabel('Time', font='Times New Roman', fontsize=18)
            ax.set_ylabel(r'Amplitude $[m^2/s^4/Hz]$ [dB]', font='Times New Roman', fontsize=18)
            ax.set_title(f'Spectrum at {T0}s - {', '.join(stations)} ({component})', font='Times New Roman', fontsize=20, fontweight='bold')
            ax.grid('minor')
            ax.set_xlim(min(times).datetime, max(times).datetime)
            ax.set_ylim(-14, -9)

            xticks = ax.get_xticks()
            ax.xaxis.set_major_locator(FixedLocator(xticks))
            ax.set_xticklabels(xticks, rotation=45, font='Times New Roman', fontsize=16, color='navy')

            ax.set_yticks(ax.get_yticks())
            ax.set_yticklabels(ax.get_yticks(), font='Times New Roman', fontsize=16, color='red')
            ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
            date_form = DateFormatter("%Y-%b-%d")
            ax.xaxis.set_major_formatter(date_form)
            fig, ax = plot_hurracaine_stages(fig, ax)


        ax.plot(times, spectrum_at_T0, c=c, linewidth=1, label =f'{stations[k].upper()} ({distance_to_touchdown:.0f}km)')
     
        t_touch = core.get_touchdown_time() 
        ax.axvline(t_touch, color='black', linestyle='--')
        ax.legend()

        #ax.axvspan(datetime(2023,10,23,3,0), datetime(2023,10,24,9,0), color='green', alpha=0.35) # Tropical storm 
        #ax.axvspan(datetime(2023,10,24,9,0), datetime(2023,10,24,19,0), color='orange', alpha=0.35)
        #ax.axvspan(datetime(2023,10,24,19,0), datetime(2023,10,25,6,0), color='purple', alpha=0.35)
        #ax.axvspan(datetime(2023,10,25,6,0), datetime(2023,10,25,15,0), color='orange', alpha=0.35)
        #ax.axvspan(datetime(2023,10,25,15,0), datetime(2023,10,25,21,0), color='green', alpha=0.35) # Tropical storm 

    filenameout = os.path.join('figures', f'spectrum_at_period_{T0}s', f'{'_'.join(stations)}_{component}.png')
    fig.savefig(filenameout, bbox_inches='tight')
    print(f'Saved {filenameout}')
    plt.close(fig)
        #fig.show()
