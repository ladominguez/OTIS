import numpy as np
from obspy.core import read
from matplotlib import pyplot as plt
from tqdm import tqdm
from utils import downsample_array, get_spectrum, plot_spectrum
from pympler import asizeof
import time
from datetime import datetime
import multiprocessing as mp
import pickle


npts = 2**16
station = 'caig'
component = 'HHN'
T_min = 0.5
T_max = 10
overlap = 1.0
input_file = '/'.join(['data',station,'.'.join([station,component,'sac'])])
spectrum_filename = 'spectrum_2023-10-16_03:50:17_2023-10-17_03:30:12.pkl'


def get_windows(stream, win):
    sub_windows = [window for window  in stream[0].slide(window_length=win, step=win*overlap)]
    return sub_windows

def get_spectrum_parallel_processing(cores=6):
    print('Reading ' + input_file + ' ...')
    sac = read(input_file)
    delta = round(sac[0].stats.delta * 100) / 100
    span_sec = sac[0].stats.endtime - sac[0].stats.starttime

    win = delta * (npts - 1)
    sub_windows = get_windows(sac,win)
    inputs = zip(sub_windows, [npts for _ in range(len(sub_windows))])

    t0 = time.time()

    with mp.Pool(processes = cores) as pool:
        results = list(pool.starmap(get_spectrum, inputs))
    t1 = time.time()

    print('Execution took {:.4f}'.format(t1 - t0))
    return results

# Write a function that saves the output of the function get_spectrum_parallel_processing to a binary file sing pickle
def save_spectrum2file(results):
    times = [t.timestamp for t, _, _ in results]
    min_time = datetime.utcfromtimestamp(min(times))
    max_time = datetime.utcfromtimestamp(max(times))
    min_time = min_time.strftime('%Y-%m-%d_%H:%M:%S')
    max_time = max_time.strftime('%Y-%m-%d_%H:%M:%S')
    filename = '_'.join(['spectrum',
                         datetime.utcfromtimestamp(min(times)).strftime('%Y-%m-%d_%H:%M:%S'),
                         datetime.utcfromtimestamp(max(times)).strftime('%Y-%m-%d_%H:%M:%S')]) + '.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(results, f)
    return None

# Write a function that reads the output of the function get_spectrum_parallel_processing from a binary file sing pickle
def read_spectrum2file(filename):
    with open(filename, 'rb') as f:
        results = pickle.load(f)
    return results

# Write a function to extract the minimum and maximum values of a list containing UTCDateTime objects
def get_min_max_times(times):
    min_time = min(times)
    max_time = max(times)
    return min_time, max_time



if __name__ == '__main__':
    results = get_spectrum_parallel_processing(cores=8)
    save_spectrum2file(results) 
    #results = read_spectrum2file(spectrum_filename)
    #plot_spectrum(results)

