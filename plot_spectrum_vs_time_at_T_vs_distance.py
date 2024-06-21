import numpy as np
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import glob
from otis import core
from otis.plotting.tools import get_spectrum_from_results, get_periods_from_results, get_average_spectrum, get_periods_from_results, get_index_from_period 
from otis.plotting.plot import plot_hurracaine_stages, plot_touchdown
from matplotlib.pyplot import cm
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FixedLocator
from datetime import datetime
from ssn import get_station_by_name
from geopy.distance import great_circle
from matplotlib.ticker import FormatStrFormatter


component = 'HHZ'
T0 = 4 
suffix='2'
spectrum_files = glob.glob(os.path.join('spectra', '??ig',f'spectrum*{component}_*.pkl'))
spectrum_files.sort()
colormap_name = 'inferno'
distancia_maxima = 500
t_xaxis_min = datetime(2023, 10, 24)
#t_xaxis_max = datetime(2023, 10, 26)
t_xaxis_max = core.get_touchdown_time()

if __name__ == '__main__':

    lat_touchdown, lon_touchdown = core.get_touchdown_coordinates()
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))
    for k, file in enumerate(spectrum_files):
        print(file)
        results, config = core.read_spectrum2file(file)
        times = core.get_times_from_results_datetime(results)
        station = config['station']['name']
        component = config['station']['component']
        stla, stlo = get_station_by_name(station)
        periods = get_periods_from_results(results)
        spectrum = get_spectrum_from_results(results)
        spectrum = np.array([np.clip(result[1], -15, None) for result in results])
        ind_T0 = get_index_from_period(results, T0)
        distance_to_touchdown = great_circle((stla, stlo), (lat_touchdown, lon_touchdown)).kilometers
        spectrum_at_T0 = spectrum[:,ind_T0]
        if distance_to_touchdown < distancia_maxima:
            ax.scatter(times, np.full_like(times, distance_to_touchdown), c=spectrum_at_T0, cmap=colormap_name, s=12, marker='s', vmin=-14, vmax=-9)
        ax.annotate(station, (t_xaxis_max, distance_to_touchdown), fontsize=8, color='black')
    #cbar = plt.colorbar(cm.ScalarMappable(cmap=colormap_name), ax=ax, orientation='vertical', label='Amplitude (dB)')
    
    ax.set_xlabel('Time')
    ax.set_xlim([t_xaxis_min, t_xaxis_max])
    xticks = ax.get_xticks()
    ax.xaxis.set_major_locator(FixedLocator(xticks))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%dkm'))
    ax.set_xticklabels(xticks, rotation=45)
    ax.set_ylabel('Distance to touchdown')
    date_form = DateFormatter("%Y-%b-%d, %H:%M")
    ax.xaxis.set_major_formatter(date_form)
    fig, ax = plot_touchdown(fig, ax, core.get_touchdown_time(), color='blue')
    fig.savefig(f'spectrum_at_period_{T0}s_{component}_vs_distance.png', bbox_inches='tight', dpi=400)
    print(f'Saved spectrum_at_period_{T0}s_{component}_vs_distance.png')
    #fig.show()
