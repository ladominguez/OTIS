import glob
import os 
from otis import core
from otis.plotting.tools import get_spectrum_from_results, get_index_from_period 
from matplotlib import pyplot as plt
from datetime import datetime

component = 'HHZ'
stations = ['CAIG', 'PZIG']
T0 = 4.0

t_xaxis_min = datetime(2023, 10, 24)
#t_xaxis_max = datetime(2023, 10, 26)
t_xaxis_max = core.get_touchdown_time()

if __name__ == '__main__':
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))
    for station in stations:
        spectrum_file = glob.glob(os.path.join('spectra',station.lower(),f'spectrum*{component}_*.pkl'))
        if len(spectrum_file) == 0:
            print(f'No spectrum file found for {station}')
            raise FileNotFoundError
        
        if len(spectrum_file) > 1:
            print(f'Multiple spectrum files found for {station}')
            raise FileNotFoundError
        
        results, config = core.read_spectrum2file(spectrum_file[0])
        times = core.get_times_from_results_datetime(results)
        spectrum = get_spectrum_from_results(results)
        ind_T0 = get_index_from_period(results, T0)
        spectrum_at_T0 = spectrum[:,ind_T0]

        ax.plot(times, spectrum_at_T0, label=station)
        ax.legend()
        ax.set_xlim([t_xaxis_min, t_xaxis_max])
        filename_out = 'compare_' + '_'.join(stations) + '.png'
        fig.savefig(filename_out, dpi=400)
        print(f'Saved in {filename_out}')

        
