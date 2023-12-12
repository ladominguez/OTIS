from mtspec import mtspec
import pygmt
import numpy as np

T_min = 0.5
T_max = 10

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
    Aspec_max = max(max(spec) for spec in spectrum)
    print(Aspec_max)

    fig = pygmt.Figure()
    with pygmt.config(MAP_GRID_PEN_PRIMARY='3p,black,--',
                      MAP_GRID_PEN_SECONDARY='3p,black,--',
                      FONT_ANNOT_SECONDARY='12p,Palatino-Roman,black',
                      FONT_ANNOT_PRIMARY='12p,Palatino-Roman,black',
                      FONT_LABEL='12p,Palatino-Roman,black',
                      FORMAT_CLOCK_MAP="hh:mm",
                      FORMAT_DATE_MAP="o dd,yyyy",
                      FORMAT_TIME_SECONDARY_MAP="abbreviated"):

        fig.basemap(
            projection="X12c/5c",
            region=[
                times.min(),
                times.max(),
                0,
                6
            ],
            frame=["WSen", "sxa1D", "pxa6Hf1Hg1H+lTime",
                   'sya1f0.5g0.5+lMagnitude']
        )

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

    Aspec = np.log10(spec_down)

    time = data.stats.starttime + (data.stats.endtime - data.stats.starttime)
    return time, spec
