from matplotlib import pyplot as plt
import pandas as pd

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
    return time, path['latitude'], path['longitude']

if __name__ == "__main__":
    time, latitude, longitude = read_path('hurracaine_path.dat')
    pass