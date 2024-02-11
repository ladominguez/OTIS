from matplotlib import pyplot as plt
import pandas as pd
from geopy.distance import great_circle

def plot_data(data, title, xlabel, ylabel):
    plt.plot(data)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()
    return  

def read_stations_ssn(filename='./otis/stations_ssn.dat'):
    stations = pd.read_csv(filename, delim_whitespace=True,names=['station','latitude','longitude'],index_col=0)
    return stations

def read_path(filename):
    path = pd.read_csv(filename, delim_whitespace=True, 
                       names = ['time','latitude','longitude'],
                       parse_dates=['time'],
                       date_format='%Y/%m/%dT%H:%M:%S',
                       dtype={'time': str, 'latitude':float, 'longitude':float})
    time = pd.to_datetime(path['time'])
    return time, path

def distance_to_station(latitude, longitude, path):
    distances = []
    for _, row in path.iterrows():
        distances.append(great_circle((latitude, longitude), (row['latitude'], row['longitude'])).km)
    return distances


if __name__ == "__main__":
    station = 'CAIG'
    stations = read_stations_ssn()
    latitude = stations.loc[station, 'latitude']
    longitude = stations.loc[station, 'longitude']

    time, path = read_path('hurracaine_path.dat')

    distances = distance_to_station(latitude, longitude, path)
    print(distances)
    pass
