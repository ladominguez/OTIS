import numpy as np
from utils import *
import warnings

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)


#npts = 2**16
#station = 'daig'
#component = 'HHZ'
#T_min = 0.5
#T_max = 10
#overlap = 1.0
#spectrum_filename = 'spectra/caig/spectrum_caig_HHZ_2023-10-16_03:50:17_2023-10-26_23:58:32.pkl'



#def get_min_max_times(times):
#    min_time = min(times)
#    max_time = max(times)
#    return min_time, max_time

def get_average_spectrum(spectrum, index1, index2):
    return None

if __name__ == '__main__':
    config = load_configuration('configuration.ini')
    results = get_spectrum_parallel_processing(config, cores=8)
    save_spectrum2file(results,config['station']['name'],config['station']['component']) 
    #results = read_spectrum2file(spectrum_filename)
    #plot_spectrum(results)

            