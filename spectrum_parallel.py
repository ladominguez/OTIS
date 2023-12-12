import numpy as np
from obspy.core import read
from matplotlib import pyplot as plt
from tqdm import tqdm
from utils import downsample_array, get_spectrum, plot_spectrum
from pympler import asizeof
import time
import multiprocessing as mp



npts = 2**16
station = 'caig'
component = 'HHN'
T_min = 0.5
T_max = 10
overlap = 1.0
input_file = '/'.join(['data',station,'.'.join(['short',station,component,'sac'])])



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


if __name__ == '__main__':
    results = get_spectrum_parallel_processing()
    plot_spectrum(results) 
    #save_times2file(times)
