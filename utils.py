from mtspec import mtspec
import pygmt
import numpy as np

T_min = 0.5
T_max = 10
# create a color table using the minimum and maximum values
#def create_color_table(min_value, max_value, cmap_name="matlab/hot"):
#    color_table = pygmt.makecpt(cmap_name="matlab/hot", series=[min_amp, max_amp], reverse=True)
#    return color_table


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

def plot_spectrum(results):
    times = [result[0] for result in results]
    spectrum = [result[1] for result in results]
    period = [result[2] for result in results]
    Aspec_max = max(max(spec) for spec in spectrum)
    Aspec_min = min(min(spec) for spec in spectrum)
    

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

