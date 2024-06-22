import numpy as np
from obspy.core import read
import time
import multiprocessing as mp
from pympler import asizeof

def downsample_array(arr, factor):
    """
    Downsample a 1D NumPy array using averaging.

    Parameters:
    - arr: NumPy array
    - factor: Downsampling factor

    Returns:
    - Downsampled array
    """
    if factor <= 0:
        raise ValueError("Downsampling factor must be greater than 0")

    # Calculate the new length of the downsampled array
    new_length = len(arr) // factor

    # Reshape the array to a 2D array with the new length
    reshaped_arr = arr[:new_length * factor].reshape((new_length, factor))

    # Take the mean along the specified axis (axis=1 means along columns)
    downsampled_arr = np.mean(reshaped_arr, axis=1)

    return downsampled_arr

def get_spectrum(data, npts, T_min, T_max):
    from mtspec import mtspec
    #npts = 2**16
    delta = round(data.stats.delta * 100) / 100
    span_sec = data.stats.endtime - data.stats.starttime

    win = delta * (npts - 1)
    
    spec, freq, jackknife, _, _ = mtspec(data=data, delta=delta, time_bandwidth=3.5, 
                                      number_of_tapers=5, nfft=npts, statistics=True)

    freq = np.delete(freq, 0)
    spec = np.delete(spec, 0)

    T    = 1/freq
    ind = np.where((T >= T_min) & (T <= T_max))[0]

    T_down = T[ind]
    freq_down = freq[ind]
    spec_down = spec[ind]

    spec_down = np.log10(spec_down)

    time = data.stats.starttime + (data.stats.endtime - data.stats.starttime)
    return time, spec_down, T_down

def get_spectrum_parallel_processing(config, cores=6):
    station = config['station']['name']
    component = config['station']['component']
    T_min = eval(config['spectrum']['T_min'], {'__builtins__': None}, {})
    T_max = eval(config['spectrum']['T_max'], {'__builtins__': None}, {})
    npts = eval(config['spectrum']['npts'], {'__builtins__': None}, {})
    overlap = eval(config['spectrum']['overlap'], {'__builtins__': None}, {})
    input_file = '/'.join(['data',station,'.'.join(['IG',station.lower(),component,'corrected.sac'])])


    print('Reading ' + input_file + ' ...')
    sac = read(input_file)
    delta = round(sac[0].stats.delta * 100) / 100
    span_sec = sac[0].stats.endtime - sac[0].stats.starttime

    win = delta * (npts - 1)
    sub_windows = get_windows(sac,win, overlap)
    inputs = zip(sub_windows, [npts for _ in range(len(sub_windows))], 
                 [T_min for _ in range(len(sub_windows))], 
                 [T_max for _ in range(len(sub_windows))] )

    t0 = time.time()

    with mp.Pool(processes = cores) as pool:
        results = list(pool.starmap(get_spectrum, inputs))
    t1 = time.time()

    print('Execution took {:.4f}'.format(t1 - t0))
    print('Memory usage: {:.4f} MB'.format(asizeof.asizeof(results)/1024/1024))
    print('Number of days processed: {:.1f} days'.format(span_sec/86400))
    return results

def get_windows(stream, win, overlap):
    sub_windows = [window for window  in stream[0].slide(window_length=win, step=win*overlap)]
    return sub_windows


# This function that saves the output of the function get_spectrum_parallel_processing to a binary file sing pickle

