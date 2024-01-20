#from mtspec import mtspec
#from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FixedLocator
import pickle
from obspy.core import read
import os
from datetime import datetime
import time
import multiprocessing as mp
from pympler import asizeof
import configparser

def load_configuration(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def print_configuration(config):
    for section in config.sections():
        print(f"[{section}]")
        for key in config[section]:
            print(f"{key} = {config[section][key]}")
        print()

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

def get_average_spectrum(results, index1, index2):
    """
    Get the average spectrum between two indices.

    Parameters:
    - spectrum: 2D NumPy array containing the spectrum
    - index1: First index
    - index2: Second index

    Returns:

    """
    if index1 > index2:
        raise ValueError("index1 must be less than or equal to index2")
    
    if index2 > len(results):
        raise ValueError("index2 must be less than or equal to the length of the spectrum")
    spectrogram = get_spectrum_from_results(results)
    sums = np.sum(spectrogram[index1:index2], axis=1)
    Q1 = np.percentile(sums, 25, axis=0)
    Q3 = np.percentile(sums, 75, axis=0)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Remove outliers
    index_remove = np.where((sums < lower_bound) | (sums > upper_bound))[0]
    #spectrogram[index1:index2][index_remove] = np.nan
    
    return np.delete(spectrogram[index1:index2], index_remove,0).mean(axis=0)

def get_spectrum_from_results(results):
    return np.array([result[1] for result in results])

def get_periods_from_results(results):
    return np.array([result[2] for result in results])

def get_times_from_results(results):
    return np.array([result[0] for result in results])

def get_time_from_index(results, index):
    return results[index][0]
def get_times_from_results(results):
    return  [result[0] for result in results]
# This function that reads the output of the function get_spectrum_parallel_processing from a binary file sing pickle
def read_spectrum2file(filename):
    with open(filename, 'rb') as f:
        results, configuration = pickle.load(f)
    return results, configuration

def plot_spectrum(results, config, plot_fig=True, demean_plot=False):
    """
    Plot the spectrum of seismic data.

    Args:
        results (list): List of tuples containing the results of the spectrum analysis.
            Each tuple should have the format (time, spectrum, period).
        config (dict): Configuration settings for the plot.
            It should contain the keys 'station' and 'spectrum'.
        plot_fig (bool, optional): Whether to display the plot. Defaults to True.

    Returns:
        tuple: A tuple containing the figure and axis objects of the plot.

    """
    times = [result[0] for result in results]
    if demean_plot:
        spectra = get_spectrum_from_results(results)
    else:
        spectra = [np.clip(result[1], -1, None) for result in results]
    periods = [result[2] for result in results]
    Aspec_max = max(max(spec) for spec in spectra)
    # The next 3 lines remove the -inf values from the spectra, and then calculate the minimum value
    Aspec_min = np.min(spectra, axis = 1) 
    Aspec_min_no_inf = np.where(Aspec_min == -np.inf, np.nan, Aspec_min)
    Aspec_min = np.nanmin(Aspec_min_no_inf, axis = 0)
    
    station = config['station']['name']
    component = config['station']['component']
    T_min = eval(config['spectrum']['T_min'], {'__builtins__': None}, {})
    T_max = eval(config['spectrum']['T_max'], {'__builtins__': None}, {})

    # create a spectrogram plot using matplotlib
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_title(station.upper() + ' - ' + component)
    ax.set_xlabel('Time')
    ax.set_ylabel('Period')
    ax.set_yscale('log')
    ax.set_ylim(T_min, T_max)
    ax.set_xlim(min(times).datetime, max(times).datetime)
    ax.set_facecolor('black')
    xticks = ax.get_xticks()
    ax.xaxis.set_major_locator(FixedLocator(xticks))
    ax.set_xticklabels(xticks, rotation=45)

    date_form = DateFormatter("%Y-%b-%d")
    ax.xaxis.set_major_formatter(date_form)

    for ti, period, spectrum in zip(times, periods, spectra):
        t = [ti.datetime for _ in range(len(period))]
        if demean_plot:
            Aspec_max_abs = max(abs(Aspec_max), abs(Aspec_min))
            ax.scatter(t, period, c=spectrum, cmap='seismic', vmin=-Aspec_max_abs, vmax=Aspec_max_abs, s=12, marker='s')
        else:
            ax.scatter(t, period, c=spectrum, cmap='hot', vmin=Aspec_min, vmax=Aspec_max, s=12, marker='s')

    if plot_fig:
        plt.show()

    return fig, ax

def plot_average_box(fig, ax, t0, t1, color='white'):
    # make the outline of the box black
    ax.axvspan(t0.datetime, t1.datetime, linewidth=3, 
               edgecolor=color, facecolor='none', clip_on=True)
    #ax.axvspan(t0.datetime, t1.datetime, linewidth=3)
    return fig, ax
def remove_average_spectrum(results, index1, index2):
    demeaned = get_spectrum_from_results(results) - get_average_spectrum(results, index1, index2)
    return [(result[0], demean, result[2]) for result, demean in zip(results, demeaned)]

def remove_outliers(results, threshold=0.5):
    """
    Remove outliers from a list of results.

    Args:
        results (list): List of tuples containing the results of the spectrum analysis.
            Each tuple should have the format (time, spectrum, period).
        threshold (float, optional): Threshold for removing outliers. Defaults to 0.5.

    Returns:
        list: List of tuples containing the results of the spectrum analysis with outliers removed.

    """
    spectra = [result[1] for result in results]
    periods = [result[2] for result in results]
    # Calculate the mean and standard deviation of each period
    mean = np.array([np.mean(spec) for spec in spectra])
    std = np.array([np.std(spec) for spec in spectra])
    # Calculate the z-score for each spectrum
    z_scores = [(spec - mean) / std for spec in spectra]
    # Remove outliers
    results = [result for result, z_score in zip(results, z_scores) if np.all(np.abs(z_score) < threshold)]
    return results

def get_spectrum(data, npts, T_min, T_max):
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
    input_file = '/'.join(['data',station,'.'.join([station,component,'sac'])])


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
def save_spectrum2file(results, config):
    times = [t.timestamp for t, _, _ in results]
    min_time = datetime.utcfromtimestamp(min(times))
    max_time = datetime.utcfromtimestamp(max(times))
    min_time = min_time.strftime('%Y-%m-%d_%H:%M:%S')
    max_time = max_time.strftime('%Y-%m-%d_%H:%M:%S')
    station = config['station']['name']
    component = config['station']['component'] 

    filename = '_'.join(['spectrum', station, component,
                         datetime.utcfromtimestamp(min(times)).strftime('%Y-%m-%d_%H:%M:%S'),
                         datetime.utcfromtimestamp(max(times)).strftime('%Y-%m-%d_%H:%M:%S')]) + '.pkl'
    # check in the directory spectra/station already exists, if not create it
    if not os.path.exists(os.path.join('spectra',station)):
        os.makedirs(os.path.join('spectra',station))
 
    output_file = os.path.join('spectra',station,filename)  
    with open(output_file, 'wb') as f:
        pickle.dump([results, config], f)
    print('Spectrum saved to ' + output_file)
    return None

def save_times2file(times, filename='times.txt'):
    date_strings = [t.strftime("%Y-%m-%d %H:%M:%S") for t in times]
    with open(filename, "w") as file:
        for date_string in date_strings:
            file.write(f"{date_string}\n")
    return None

def save_figure(fig, station, component, resolution=300):
    
    file_figure = '_'.join(['spectrum', station, component]) + '.png'
                            #datetime.utcfromtimestamp(min(times)).strftime('%Y-%m-%d_%H:%M:%S'),
                            #datetime.utcfromtimestamp(max(times)).strftime('%Y-%m-%d_%H:%M:%S')]) + '.png'
    file_figure = os.path.join('figures',file_figure)
    fig.savefig(file_figure, dpi=resolution)