import numpy as np
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import pandas as pd
import glob
from otis import core
from otis.plotting.tools import get_spectrum_from_results, get_periods_from_results, get_average_spectrum
from matplotlib.pyplot import cm
from geopy.distance import great_circle
from ssn import get_station_by_name

components = 'HHN'
spectrum_files = glob.glob(os.path.join('spectra', '??ig','spectrum*' + component + '*.pkl'))
spectrum_files.sort()

def calculate_bearing(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlon = lon2 - lon1
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    bearing = np.degrees(np.arctan2(y, x))
    bearing = (bearing + 360) % 360
    return bearing

if __name__ == '__main__':
    df = pd.DataFrame(columns=['station', 'component', 'period', 'max_value', 'distance_to_touchdown', 
                               'azimuth'])
    lat_touchdown, lon_touchdown = core.get_touchdown_coordinates()

    for component in components:
        spectrum_files = glob.glob(os.path.join('spectra', '??ig','spectrum*' + component + '*.pkl'))
        spectrum_files.sort()
        for file in spectrum_files:
            #print('file:', file)
            station = file.split('/')[1]
            stla, stlo = get_station_by_name(station)
            results, config = core.read_spectrum2file(file)
            periods = get_periods_from_results(results)
            spectrum = get_spectrum_from_results(results)
            t_touchdown = core.get_touchdown_UTCDatetime()
            t_touchdown_index = core.get_index_from_time(results, t_touchdown)
            spectrum = get_spectrum_from_results(results)
            spectrum_at_touchdown = spectrum[t_touchdown_index,:]
            periods_at_touchdown = periods[t_touchdown_index,:]
            max_value = np.max(spectrum_at_touchdown)
            max_value_index = np.argmax(spectrum_at_touchdown)
            distance_to_touchdown = great_circle((stla, stlo), (lat_touchdown, lon_touchdown)).kilometers
            azimuth = calculate_bearing((lat_touchdown, lon_touchdown), (stla, stlo) )
            print('coordinates:', stla, stlo, ' touchdown: ', lat_touchdown, lon_touchdown, 'distance to touchdown:', distance_to_touchdown, 'azimuth:', azimuth)
            print('Maximum value:', max_value, ' at period:', periods_at_touchdown[max_value_index], ' for station ', station )
            df.loc[len(df)] = [station, component, periods_at_touchdown[max_value_index], max_value, distance_to_touchdown,
                           azimuth]
        #plt.plot(periods_at_touchdown, spectrum_at_touchdown, label=os.path.basename(file))
        #plt.plot(periods_at_touchdown[max_value_index], max_value, 'ro')
        plt.scatter(df['distance'], df['max_value'], c=df['max_value'], cmap='viridis')
        print(df)
        plt.xscale('log')
        plt.yscale('log')
    
