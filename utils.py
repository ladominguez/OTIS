from mtspec import mtspec
import numpy as np
import time
from obspy.core import read
import multiprocessing as mp
import pickle
from pympler import asizeof
from datetime import datetime
from matplotlib import pyplot as plt

T_min = 0.5
T_max = 10
# create a color table using the minimum and maximum values
#def create_color_table(min_value, max_value, cmap_name="matlab/hot"):
#    color_table = pygmt.makecpt(cmap_name="matlab/hot", series=[min_amp, max_amp], reverse=True)
#    return color_table

def get_windows(stream, win, overlap):
    sub_windows = [window for window  in stream[0].slide(window_length=win, step=win*overlap)]
    return sub_windows

def get_spectrum_parallel_processing(input_file, npts, overlap, T_min, T_max, cores=6):
    print('Reading ' + input_file + ' ...')
    sac = read(input_file)
    delta = round(sac[0].stats.delta * 100) / 100
    span_sec = sac[0].stats.endtime - sac[0].stats.starttime

    win = delta * (npts - 1)
    sub_windows = get_windows(sac, win, overlap)
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
    min_time = datetime.utcfromtimestamp(min(times)).strftime('%Y-%m-%d_%H:%M:%S')
    max_time = datetime.utcfromtimestamp(max(times)).strftime('%Y-%m-%d_%H:%M:%S')
    filename = './spectra/' + '_'.join(['spectrum',min_time,max_time]) + '.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(results, f)
    return filename

# Write a function that reads the output of the function get_spectrum_parallel_processing from a binary file sing pickle
def read_spectrum2file(filename):
    with open(filename, 'rb') as f:
        results = pickle.load(f)
    return results

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

def save_times2file(times, filename='times.txt'):
    date_strings = [t.strftime("%Y-%m-%d %H:%M:%S") for t in times]
    with open(filename, "w") as file:
        for date_string in date_strings:
            file.write(f"{date_string}\n")
    return None

def plot_spectrum(results, T_min, T_max):
    times = [result[0] for result in results]
    spectrum = [result[1] for result in results]
    period = [result[2] for result in results]
    Aspec_max = max(max(spec) for spec in spectrum)
    Aspec_min = min(min(spec) for spec in spectrum)

    fig, ax = plt.subplots(figsize=(10, 10))
    for t, spec, T in zip(times, spectrum, period):
        ax.plot(t, spec, color='k', alpha=0.2)  
    ax.set_xlabel('Time')
    ax.set_ylabel('Period')
    ax.set_title('Spectrum')
    ax.set_xlim(min(times), max(times))
    ax.set_ylim(T_min, T_max)
    plt.show()
    return None

    

def import_spectrum(filename):
    with open(filename, 'rb') as f:
        results = pickle.load(f)
    return results

def get_spectrum(data, npts):
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

