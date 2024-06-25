import numpy as np
import os
import matplotlib as mpl
from matplotlib import pyplot as plt
import pandas as pd
import glob
from otis import core
from otis.plotting.tools import get_spectrum_from_results, get_periods_from_results, get_average_spectrum
from otis.plotting.plot import plot_map
from matplotlib.pyplot import cm
from geopy.distance import great_circle
from ssn import get_station_by_name

components = ['HHZ']
CPT_max_value = './cpt/max_values_red2green.cpt'
CPT_max_value_relative = './cpt/max_values_relative_hot.cpt'
CPT_azimuth = './cpt/azimuth.cpt'
CPT_distance = './cpt/distance.cpt'
CPT_period_max_relative = './cpt/period_max_relative.cpt'

field = 'max_value_relative'
isolines = True

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
def get_datafame(saving = False, filename = 'data/summary_data.pkl'):
    df = pd.DataFrame(columns=['station', 'component', 'stla', 'stlo', 'period', 'max_value', 
                               'max_value_relative', 'period_max_relative', 'distance_to_touchdown', 
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
            average_spectrum = get_average_spectrum(results, 20, 240)
            relative_spectrum = (10**spectrum_at_touchdown-10**average_spectrum) / 10**average_spectrum
            max_value_relative = np.max(relative_spectrum)
            max_value_relative_index = np.argmax(relative_spectrum)

            distance_to_touchdown = great_circle((stla, stlo), (lat_touchdown, lon_touchdown)).kilometers
            azimuth = calculate_bearing((lat_touchdown, lon_touchdown), (stla, stlo) )
            df.loc[len(df)] = [station, component, stla, stlo, periods_at_touchdown[max_value_index], max_value, 
                               max_value_relative, periods_at_touchdown[max_value_relative_index], distance_to_touchdown,
                           azimuth]
            
    if saving:
        print('Saving data to:', filename)
        df.to_pickle(filename)
    
    return df

def read_summary_data(filename = 'data/summary_data.pkl'):
    return pd.read_pickle(filename)

def plot_data(fig, df, field='max_value_relative', station_labels = False):
    # Run using conda enviroment pygmt 
    for _, row in df.iterrows():
        station = row['station'].upper()
        component = row['component']
        stla = row['stla']
        stlo = row['stlo']
        period_max_relative = row['period_max_relative']
        max_value = row['max_value']
        max_value_relative = row['max_value_relative']
        distance_to_touchdown = row['distance_to_touchdown']
        azimuth = row['azimuth']
        if station_labels:
            fig.text(x=stlo, y=stla, text=station, font='8p,Times-Roman,black', justify='LM', offset='0.2c')
        match field:
            case 'max_value':
                print('max_value: ', max_value)
                fig.plot(x=stlo, y=stla, style='c0.35c', pen='1p,black',cmap=CPT_max_value, zvalue=max_value, fill="+z")
            case 'max_value_relative':
                fig.plot(x=stlo, y=stla, style='c0.35c', pen='1p,black',cmap=CPT_max_value_relative, zvalue=max_value_relative, fill="+z")
            case 'distance_to_touchdown':
                fig.plot(x=stlo, y=stla, style='c0.35c', pen='1p,black',cmap=CPT_distance, zvalue=distance_to_touchdown, fill="+z")
            case 'azimuth':
                fig.plot(x=stlo, y=stla, style='c0.35c', pen='1p,black',cmap=CPT_azimuth, zvalue=azimuth, fill="+z")
            case 'period_max_relative':
                fig.plot(x=stlo, y=stla, style='c0.35c', pen='1p,black',cmap=CPT_period_max_relative, zvalue=period_max_relative, fill="+z")
            case _:
                raise ValueError(f'Field {field} not recognized')
    match field:
        case 'max_value':
            fig.colorbar(cmap=CPT_max_value, position="jBL+o0.15i/1.0i+w1.5i/0.10i+h", frame=["xa2fa1+lMax value (dB)"])
        case 'max_value_relative':
            fig.colorbar(cmap=CPT_max_value_relative, position="jBL+o0.32i/1.0i+w1.8i/0.10i+h", frame=["xa100fa50+lTimes relative to average"])
        case 'period_max_relative':
            fig.colorbar(cmap=CPT_period_max_relative, position="jBL+o0.32i/1.0i+w1.8i/0.10i+h", frame=["xa0.5f0.25+lPeriod (s)"])
        case '_':
            pass

    return fig

if __name__ == '__main__':

        #plt.plot(periods_at_touchdown, spectrum_at_touchdown, label=os.path.basename(file))
        #plt.plot(periods_at_touchdown[max_value_index], max_value, 'ro')
        #plt.scatter(df['distance'], df['max_value'], c=df['max_value'], cmap='viridis')
        #plt.xscale('log')
        #plt.yscale('log')
    #df = get_datafame(saving=True)
    df = read_summary_data()
    print(df)

    fig = plot_map(quick=False, isolines=isolines, tmvb=True)
    fig = plot_data(fig, df, field=field, station_labels=True)
    #fig.text(x=0.5, y=0.95, text=f"{field.capitalize()} - {components}")
    if isolines:
        filename_out = f'figures/map/map_{field}_{components[0]}.png'
    else:
        filename_out = f'figures/map/map_{field}_{components[0]}_no_isolines.png'
    print('Saving figure to:', filename_out)
    fig.savefig(filename_out, dpi=300)
    pass
