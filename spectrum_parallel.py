import numpy as np
from obspy.core import read
from matplotlib import pyplot as plt
from tqdm import tqdm
from utils import downsample_array, get_spectrum
from pympler import asizeof
import time
import multiprocessing as mp



npts = 2**16
input_file = 'data/caig/caig.HHN.sac'
T_min = 0.5
T_max = 10
overlap = 1.0



def get_windows(stream, win):
    sub_windows = [window for window  in stream[0].slide(window_length=win, step=win*overlap)]
    return sub_windows

def main():
    sac = read(input_file)
    sac = read(input_file)
    delta = round(sac[0].stats.delta * 100) / 100
    span_sec = sac[0].stats.endtime - sac[0].stats.starttime

    win = delta * (npts - 1)
    #trim = sac.copy()
    #trim.trim(starttime=sac[0].stats.starttime, endtime=sac[0].stats.starttime + span_sec)

    #size_in_bytes = asizeof.asizeof(sac)/2**30
    sub_windows = get_windows(sac,win)
    #size_in_bytes = asizeof.asizeof(sub_windows)/2**30
    #ti, spec = get_spectrum(sub_windows[0], npts)
    inputs = zip(sub_windows, [npts for _ in range(len(sub_windows))])

    t0 = time.time()

    with mp.Pool(processes = 8) as pool:
      results = list(pool.starmap(get_spectrum, inputs))
    t1 = time.time()
    print('Execution took {:.4f}'.format(t1 - t0))



    


if __name__ == '__main__':
    main()
