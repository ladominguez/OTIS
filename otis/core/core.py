import configparser
import pickle
from datetime import datetime
import os
from obspy.core import UTCDateTime

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

def read_spectrum2file(filename):
    with open(filename, 'rb') as f:
        results, configuration = pickle.load(f)
    return results, configuration

def get_time_from_index(results, index):
    return results[index][0]



def get_index_from_time(results, ti):
    """ti must be in UTCDateTime format"""
    times = get_times_from_results(results)
    closest_time = min(times, key=lambda x: abs(x - ti))
    index = times.index(closest_time)
    return index


def get_times_from_results(results):
    return  [result[0] for result in results]

def get_touchdown_time():
    return datetime(2023,10,25,6,0)

def get_touchdown_UTCDatetime():
    return UTCDateTime(2023,10,25,6,0)

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
