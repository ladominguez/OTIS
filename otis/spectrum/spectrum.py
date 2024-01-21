from mtspec import mtspec
from tqdm import tqdm
import numpy as np
import pickle
from obspy.core import read
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
