import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygmt
import ssn
from scipy.interpolate import interp1d
from geopy.distance import great_circle
from matplotlib.dates import DateFormatter


# Create a DataFrame
file = 'hurracaine_path.dat'
file_labels = 'hurracaine_path_labels.tmp'
trench_file = '/Users/antonio/Dropbox/gmt/trench.gmt'
TFZ_file = '/Users/antonio/Dropbox/gmt/tecto/tfz.dig'

trajectory = pd.read_csv(file, delim_whitespace=True, names=['datetime', 'lat', 'lon'], dtype = {'datetime': str, 'lat': float, 'lon': float})
trajectory['datetime'] = pd.to_datetime(trajectory['datetime'], format='%Y/%m/%dT%H:%M:%S')
trajectory_labels = pd.read_csv(file_labels, delim_whitespace=True, names=['datetime', 'lat', 'lon'], dtype = {'datetime': str, 'lat': float, 'lon': float})
trajectory_labels['datetime'] = pd.to_datetime(trajectory_labels['datetime'], format='%Y/%m/%dT%H:%M:%S')

plot_map = False
station = ['CAIG', 'DAIG', 'CRIG', 'ZIIG', 'MEIG', 'ARIG']

def interpolate_trajectory(trajectory, time_interval=10):
    x = trajectory['lat']
    y = trajectory['lon']
    t = trajectory['datetime']
    timestamps=np.array([ti.timestamp() for ti in t])
    trajectory_latitutde = np.linspace(x.min(), x.max(), time_interval)
    func = interp1d(x, y, kind='cubic')
    func_time = interp1d(x, timestamps, kind='cubic')
    trajectory_longitude = func(trajectory_latitutde)
    times_trajectory = func_time(trajectory_latitutde)
    return trajectory_latitutde, trajectory_longitude, times_trajectory

def plot_map(trajectory_latitutde, trajectory_longitude, save=False):
    # Create a figure and an axis
    fig = pygmt.Figure()
    ssn_stations = ssn.get_all_stations()

    # Set the region and projection
    region = "-108/-90/10/22"
    projection = "M8i"
    frame= ['WSne','xa4f2','ya2f2']
    fig.basemap(region=region, projection=projection, frame=frame)

    # Plot the map of Mexico
    fig.coast(land="gray", water="white", shorelines=True)
    fig.plot(data = trench_file, style="f0.5i/0.10i+l+t", pen="1p,black", fill="gray69")

    for row in ssn_stations.itertuples():
        fig.text(x=row.longitude, y=row.latitude+0.2, text=row.stnm, font='7p,Times-Bold,blue')
        if row.stnm in station:
            fig.plot(x=row.longitude, y=row.latitude, style='t0.3c', pen='1p', fill='red', label=row.stnm)
        else:
            fig.plot(x=row.longitude, y=row.latitude, style='t0.4c', pen='1p', fill='white', label=row.stnm)

    for x_text, y_text, t_text in zip(trajectory_labels['lon'], trajectory_labels['lat'], trajectory_labels['datetime']):
        fig.text(x=x_text, y=y_text, text=t_text.strftime('%b-%d %H:%M'), font='8p,Times-Bold,black',justify='BL')

    fig.plot(x=trajectory_longitude, y=trajectory_latitutde, style='c0.1c', pen='1p,black', fill='blue')
    fig.plot(x=trajectory['lon'], y=trajectory['lat'], style='c0.2c', fill='red', pen='black')
    #fig.plot(data = TFZ_file, pen="1p,black")

    if save:
        fig.savefig('hurracaine_path.png', dpi=300)
        print('Saving figure hurracaine_path.png')
    else:   
        fig.show()

#def plot_distance2station(trajectory_latitutde, trajectory_longitude, times, station):
#    pass
#    return time, distance
    # Add code here

def plot_trajectory(trajectory_latitutde, trajectory_longitude, times, stations,save=False):
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))

    for station in stations:
        lat_station, lon_station = ssn.get_station_by_name(station)
        distance = []
        for lat, lon in zip(trajectory_latitutde, trajectory_longitude):
            distance.append(great_circle((lat, lon), (lat_station, lon_station)).kilometers)

        times_datetime = pd.to_datetime(times, unit='s')
        ax.plot(times_datetime, distance, label=station,linewidth = 5, alpha = 0.5)

    date_form = DateFormatter("%b-%d, %H:%M")
    ax.set_xlabel('Time')
    ax.set_ylabel('Distance [km]')
    ax.set_title('Distance to station', fontname='Times New Roman')
    ax.xaxis.set_major_formatter(date_form)
    ax.grid()
    ax.legend()
    ax.set_xlim(times_datetime.min(), times_datetime.max())
    plt.xticks(rotation=45)

    if save:
        plt.savefig('distance_to_station.png', dpi=300,bbox_inches = 'tight')
        print('Saving figure distance_to_station.png')
    else:
        plt.show() 

    

    
if __name__ == '__main__':
    
    trajectory_latitutde, trajectory_longitude, times_trajectory = interpolate_trajectory(trajectory,100)
    plot_map(trajectory_latitutde, trajectory_longitude, save=True)
    #plot_trajectory(trajectory_latitutde, trajectory_longitude, times_trajectory, station, save=True)
    
