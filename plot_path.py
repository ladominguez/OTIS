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
    time, path = read_path('hurracaine_path.dat')

    distances = distance_to_station(25.7617, -80.1918, path)
    print(distances)
    pass
