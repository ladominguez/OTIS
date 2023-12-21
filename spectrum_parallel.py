import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm
from utils import *
import pickle


npts = 2**16
station = 'caig'
component = 'HHN'
T_min = 0.5
T_max = 10
overlap = 1.0
input_file = '/'.join(['data',station,'.'.join(['short',station,component,'sac'])])

saved_spectrum = 'spectra/spectrum_2023-10-16_03:50:17_2023-10-17_03:30:12.pkl'

if __name__ == '__main__':
    #results = get_spectrum_parallel_processing(input_file, npts, overlap, T_min, T_max)
    #save_spectrum2file(results) 
    results = import_spectrum(saved_spectrum)
    plot_spectrum(results, T_min, T_max)