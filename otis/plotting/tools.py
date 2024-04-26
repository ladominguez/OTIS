import numpy as np

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

def get_spectrum_from_results(results, clipping = -15):
    #return np.array([np.clip(result[1], clipping, None) for result in results])
    return np.array([np.clip(result[1], clipping, None) for result in results])
    #return np.array([result[1] for result in results])

def get_periods_from_results(results):
    return np.array([result[2] for result in results])

def get_index_from_period(results, T0):
    periods = get_periods_from_results(results)
    periods = periods[0,:]
    return np.abs(periods-T0).argmin()

def get_times_from_results(results):
    return np.array([result[0] for result in results])

def remove_average_spectrum(results, index1, index2):
    demeaned = get_spectrum_from_results(results) - get_average_spectrum(results, index1, index2)
    return [(result[0], demean, result[2]) for result, demean in zip(results, demeaned)]

