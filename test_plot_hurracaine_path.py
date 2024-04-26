import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygmt
import ssn
from scipy.interpolate import interp1d
#from otis.plotting.plot import plot_hurracaine_stages
from geopy.distance import great_circle
from matplotlib.dates import DateFormatter
from datetime import datetime

# Create a DataFrame
file = 'hurracaine_path.dat'
file_labels = 'hurracaine_path_labels.tmp'
trench_file = '/Users/antonio/Dropbox/gmt/trench.gmt'
TFZ_file = '/Users/antonio/Dropbox/gmt/tecto/tfz.dig'
GRDDIR='/Users/antonio/Dropbox/MEXICO_GRD/Mexico_Larger'
CPTFILE='/Users/antonio/Dropbox/BSL/CRSMEX/Presentations/SSA_meeting_2024/map_repeaters/wikifrance_mexico.cpt'
QUICK=False

trajectory = pd.read_csv(file, delim_whitespace=True, names=['datetime', 'lat', 'lon'], dtype = {'datetime': str, 'lat': float, 'lon': float})
trajectory['datetime'] = pd.to_datetime(trajectory['datetime'], format='%Y/%m/%dT%H:%M:%S')
trajectory_labels = pd.read_csv(file_labels, delim_whitespace=True, names=['datetime', 'lat', 'lon'], dtype = {'datetime': str, 'lat': float, 'lon': float})
trajectory_labels['datetime'] = pd.to_datetime(trajectory_labels['datetime'], format='%Y/%m/%dT%H:%M:%S')

plot_map = False
station = ['CAIG', 'DAIG', 'CRIG', 'ZIIG', 'MEIG', 'ARIG', 'PLIG', 'PZIG','MOIG']

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
    region = "-108/-90/10/21.5"
    projection = "M8i"
    frame= ['WSne','xa4f2','ya2f2']
    fig.basemap(region=region, projection=projection, frame=frame)

    if not QUICK:
        print('Working on grid')
        fig.grdimage(grid=GRDDIR+'/MEXICO_LARGER.nc', shading=GRDDIR+'/MEXICO_LARGERi.nc', cmap=CPTFILE,frame=True)
        print('finished grid')


    # Plot the map of Mexico
    fig.coast(water="white", shorelines=True, map_scale="jBL+w500k+o0.5c/0.5c+f+u")
    fig.plot(data = trench_file, style="f0.5i/0.10i+l+t", pen="1p,black", fill="gray69")

    for row in ssn_stations.itertuples():
        fig.text(x=row.longitude, y=row.latitude+0.2, text=row.stnm, font='7p,Times-Bold,blue')
        if row.stnm in station:
            fig.plot(x=row.longitude, y=row.latitude, style='t0.3c', pen='1p', fill='red', label=row.stnm)
        else:
            fig.plot(x=row.longitude, y=row.latitude, style='t0.4c', pen='1p', fill='white', label=row.stnm)

    for x_text, y_text, t_text in zip(trajectory_labels['lon'], trajectory_labels['lat'], trajectory_labels['datetime']):
        fig.text(x=x_text, y=y_text, text=t_text.strftime('%b-%d %H:%M'), font='8p,Times-Bold,black',justify='BL')


    #fig.plot(data = './path/01_tropical_depression.txt', pen="5p,yellow", transparency=50)
    #fig.plot(data = './path/02_tropical_storm.txt',      pen="5p,green",  transparency=50)
    #fig.plot(data = './path/03_hurracaine.txt',          pen="5p,red",    transparency=75)
    #fig.plot(data = './path/04_major_hurracaine.txt',    pen="15p,purple",  transparency=75)
    #fig.plot(data = './path/05_hurracaine_inland.txt',   pen="15p,red")
    #fig.plot(data = './path/06_tropical_storm.txt',      pen="15p,green")

    fig.plot(x=trajectory_longitude, y=trajectory_latitutde, style='c0.15c', pen='1p,black', fill='blue')
    ind = np.where(trajectory_latitutde <= 14.3) # tropical storm
    fig.plot(x=trajectory_longitude[ind], y=trajectory_latitutde[ind], style='c0.15c', pen='1p,black', fill='green')
    ind = np.where((trajectory_latitutde > 14.3) & (trajectory_latitutde <= 15.0)) # Hurracaine
    fig.plot(x=trajectory_longitude[ind], y=trajectory_latitutde[ind], style='c0.15c', pen='1p,black', fill='orange')
    ind = np.where((trajectory_latitutde > 15.0) & (trajectory_latitutde <= 16.8)) # major Hurracaine
    fig.plot(x=trajectory_longitude[ind], y=trajectory_latitutde[ind], style='c0.15c', pen='1p,black', fill='purple')
    ind = np.where((trajectory_latitutde > 16.8) & (trajectory_latitutde <= 18.1)) # Hurracaine
    fig.plot(x=trajectory_longitude[ind], y=trajectory_latitutde[ind], style='c0.15c', pen='1p,black', fill='orange')
    ind = np.where(trajectory_latitutde > 18.1) # tropical storm
    fig.plot(x=trajectory_longitude[ind], y=trajectory_latitutde[ind], style='c0.15c', pen='1p,black', fill='green')
    fig.plot(x=trajectory['lon'], y=trajectory['lat'], style='c0.25c', fill='white', pen='2p,black')

    # Markers
    fig.plot(x=-107.6, y=13.20, style='c0.35c', pen='2p,black', fill='green')
    fig.plot(x=-107.6, y=12.60, style='c0.35c', pen='2p,black', fill='orange')
    fig.plot(x=-107.6, y=12.00, style='c0.35c', pen='2p,black', fill='purple')
    fig.text(x=-107.4, y=13.20, text='Tropical storm', font='14p,Times-Roman,black',justify='ML')
    fig.text(x=-107.4, y=12.60, text='Hurracaine', font='14p,Times-Roman,black',justify='ML')
    fig.text(x=-107.4, y=12.00, text='Major Hurracaine', font='14p,Times-Roman,black',justify='ML')

    fig.plot(x=-99.88230, y=16.8640, style='c0.3c', pen='1p,black', fill='red')  # Acapulco
    fig.plot(x=-101.5515, y=17.6418, style='c0.3c', pen='1p,black', fill='green') # Zihuatanejo
    fig.plot(x=-96.49130, y=15.668, style='c0.3c', pen='1p,black', fill='blue') # Puerto Angel

    fig.text(x=-99.88230, y=16.8640, text='Acapulco', font='8p,Times-Bold,black',justify='BL',    offset='0.2c')
    fig.text(x=-101.5515, y=17.6418, text='Zihuatanejo', font='8p,Times-Bold,black',justify='BL', offset='0.2c')
    fig.text(x=-96.49130, y=15.668, text='Puerto Angel', font='8p,Times-Bold,black',justify='BL', offset='-0.3c/-0.3c')
    
    
    
    
    
    if save:
        fig.savefig('hurracaine_path.png', dpi=400)
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
    #fig, ax = plot_hurracaine_stages(fig, ax) TODO
    ax.axvspan(datetime(2023,10,23,3,0), datetime(2023,10,24,9,0), color='green', alpha=0.15) # Tropical storm 
    ax.axvspan(datetime(2023,10,24,9,0), datetime(2023,10,24,19,0), color='orange', alpha=0.15)
    ax.axvspan(datetime(2023,10,24,19,0), datetime(2023,10,25,6,0), color='purple', alpha=0.15)
    ax.axvspan(datetime(2023,10,25,6,0), datetime(2023,10,25,15,0), color='orange', alpha=0.15)
    ax.axvspan(datetime(2023,10,25,15,0), datetime(2023,10,25,21,0), color='green', alpha=0.15) # Tropical storm
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
    #plot_map(trajectory_latitutde, trajectory_longitude, save=True)
    plot_trajectory(trajectory_latitutde, trajectory_longitude, times_trajectory, station, save=True)
    
