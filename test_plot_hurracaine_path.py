import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygmt
import os 
import glob
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
iso_dirctory = '/Users/antonio/SynologyDrive/Slab2.0/'
iso_line_20km = os.path.join(iso_dirctory, 'isoline20.txt')
iso_line_40km = os.path.join(iso_dirctory, 'isoline40.txt')
iso_line_60km = os.path.join(iso_dirctory, 'isoline60.txt')
iso_line_80km = os.path.join(iso_dirctory, 'isoline80.txt')
iso_line_100km = os.path.join(iso_dirctory, 'isoline100.txt')
iso_line_120km = os.path.join(iso_dirctory, 'isoline120.txt')



TFZ_file = '/Users/antonio/Dropbox/gmt/tecto/tfz.dig'
GRDDIR='/Users/antonio/SynologyDrive/MEXICO_GRD/Mexico_All'
CPTFILE='/Users/antonio/Dropbox/BSL/CRSMEX/Presentations/SSA_meeting_2024/map_repeaters/wikifrance_mexico.cpt'
PKL_FILE = 'hurracaine_data.pkl'
QUICK=False

def get_otis_trajectory(file, file_labels):
    trajectory = pd.read_csv(file, delim_whitespace=True, names=['datetime', 'lat', 'lon'], dtype = {'datetime': str, 'lat': float, 'lon': float})
    trajectory['datetime'] = pd.to_datetime(trajectory['datetime'], format='%Y/%m/%dT%H:%M:%S')
    trajectory_labels = pd.read_csv(file_labels, delim_whitespace=True, names=['datetime', 'lat', 'lon'], dtype = {'datetime': str, 'lat': float, 'lon': float})
    trajectory_labels['datetime'] = pd.to_datetime(trajectory_labels['datetime'], format='%Y/%m/%dT%H:%M:%S')
    return trajectory, trajectory_labels

plot_map = False
#station = ['CAIG', 'DAIG', 'CRIG', 'ZIIG', 'MEIG', 'ARIG', 'PLIG', 'PZIG','MOIG', 'OXIG']

prop_cycle = plt.rcParams['axes.prop_cycle']
color_cycle = iter(prop_cycle.by_key()['color'])

def get_list_of_stations():
    return [sta.split('/')[1].upper() for sta in glob.glob(os.path.join('spectra','*ig'))]

def get_trajectories_year(year=2023):
    df = pd.read_pickle(PKL_FILE)
    return df[df['year'] == year]
    

def interpolate_trajectory(trajectory, time_interval=10):
    x = trajectory['lat']
    y = trajectory['lon']
    t = trajectory['datetime']
    timestamps=np.array([ti.timestamp() for ti in t])
    trajectory_latitude = np.linspace(x.min(), x.max(), time_interval)
    func = interp1d(x, y, kind='cubic')
    func_time = interp1d(x, timestamps, kind='cubic')
    trajectory_longitude = func(trajectory_latitude)
    times_trajectory = func_time(trajectory_latitude)
    return trajectory_latitude, trajectory_longitude, times_trajectory

#def plot_map(trajectory_latitude, trajectory_longitude, save=False):
def plot_map(*args, save=False):

    if len(args) == 2:
        trajectory_latitude, trajectory_longitude = args
    
    # Create a figure and an axis
    fig = pygmt.Figure()
    ssn_stations = ssn.get_all_stations()
    ssn_stations_filtered = ssn_stations[ssn_stations['stnm'].isin(station)]
    # Set the region and projection
    region = "-120/-90/10/32.5"
    projection = "M8i"
    frame= ['WSne','xa4f2','ya2f2']
    fig.basemap(region=region, projection=projection, frame=frame)

    if not QUICK:
        print('Working on grid')
        fig.grdimage(grid=GRDDIR+'/MEXICO_ALL.nc', shading=GRDDIR+'/MEXICO_ALLi.nc', cmap=CPTFILE,frame=True)
        print('finished grid')


    # Plot the map of Mexico
    fig.coast(water="white", shorelines=True, map_scale="jBL+w500k+o0.5c/0.5c+f+u")
    fig.plot(data = trench_file, style="f0.5i/0.10i+l+t", pen="1p,black", fill="gray69")
    fig.plot(data = iso_line_20km, pen="0.5p,black,--", transparency=50)
    fig.plot(data = iso_line_40km, pen="0.5p,black,--", transparency=50)
    fig.plot(data = iso_line_80km, pen="0.5p,black,--", transparency=50)
    fig.plot(data = iso_line_100km, pen="0.5p,black,--", transparency=50)
    fig.plot(data = iso_line_120km, pen="0.5p,black,--", transparency=50)



    for row in ssn_stations_filtered.itertuples():
        fig.text(x=row.longitude, y=row.latitude+0.2, text=row.stnm, font='7p,Times-Bold,blue')
        if row.stnm in station:
            fig.plot(x=row.longitude, y=row.latitude, style='t0.3c', pen='1p', fill='red', label=row.stnm)
        else:
            fig.plot(x=row.longitude, y=row.latitude, style='t0.4c', pen='1p', fill='white', label=row.stnm)

    if len(args) == 2:
        for x_text, y_text, t_text in zip(trajectory_labels['lon'], trajectory_labels['lat'], trajectory_labels['datetime']):
            fig.text(x=x_text, y=y_text, text=t_text.strftime('%b-%d %H:%M'), font='8p,Times-Bold,black',justify='BL')


    #fig.plot(data = './path/01_tropical_depression.txt', pen="5p,yellow", transparency=50)
    #fig.plot(data = './path/02_tropical_storm.txt',      pen="5p,green",  transparency=50)
    #fig.plot(data = './path/03_hurracaine.txt',          pen="5p,red",    transparency=75)
    #fig.plot(data = './path/04_major_hurracaine.txt',    pen="15p,purple",  transparency=75)
    #fig.plot(data = './path/05_hurracaine_inland.txt',   pen="15p,red")
    #fig.plot(data = './path/06_tropical_storm.txt',      pen="15p,green")

    if len(args) == 1:

        for _, row in trajectories.iterrows():
            fig.plot(x=row.longitudes, y=row.latitudes, pen='1p,black,-')
            fig.plot(x=row.longitudes[0], y=row.latitudes[0], style='c0.15c', pen='1p,black', fill='green')
            fig.plot(x=row.longitudes[-1], y=row.latitudes[-1], style='t0.25c', pen='1p,black', fill='red')
            fig.text(x=row.longitudes[0], y=row.latitudes[0], text=row['name'], font='8p,Times-Bold,black',justify='BL')

    if len(args) == 2: # For Otis

        fig.plot(x=trajectory_longitude, y=trajectory_latitude, style='c0.15c', pen='1p,black', fill='blue')
        ind = np.where(trajectory_latitude <= 14.3) # tropical storm
        fig.plot(x=trajectory_longitude[ind], y=trajectory_latitude[ind], style='c0.15c', pen='1p,black', fill='green')
        ind = np.where((trajectory_latitude > 14.3) & (trajectory_latitude <= 15.0)) # Hurracaine
        fig.plot(x=trajectory_longitude[ind], y=trajectory_latitude[ind], style='c0.15c', pen='1p,black', fill='orange')
        ind = np.where((trajectory_latitude > 15.0) & (trajectory_latitude <= 16.8)) # major Hurracaine
        fig.plot(x=trajectory_longitude[ind], y=trajectory_latitude[ind], style='c0.15c', pen='1p,black', fill='purple')
        ind = np.where((trajectory_latitude > 16.8) & (trajectory_latitude <= 18.1)) # Hurracaine
        fig.plot(x=trajectory_longitude[ind], y=trajectory_latitude[ind], style='c0.15c', pen='1p,black', fill='orange')
        ind = np.where(trajectory_latitude > 18.1) # tropical storm
        fig.plot(x=trajectory_longitude[ind], y=trajectory_latitude[ind], style='c0.15c', pen='1p,black', fill='green')
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

#def plot_distance2station(trajectory_latitude, trajectory_longitude, times, station):
#    pass
#    return time, distance
    # Add code here

def plot_trajectory(trajectory_latitude, trajectory_longitude, times, stations,save=False):
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 4))

    for station in stations:
        lat_station, lon_station = ssn.get_station_by_name(station)
        distance = []
        for lat, lon in zip(trajectory_latitude, trajectory_longitude):
            distance.append(great_circle((lat, lon), (lat_station, lon_station)).kilometers)

        times_datetime = pd.to_datetime(times, unit='s')
        cc = next(color_cycle)
        ax.plot(times_datetime, distance, color = cc, label=station,linewidth = 5, alpha = 0.5)
        ax.plot(times_datetime, distance, color = cc, label='_Hidden',linewidth = 1)

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
    station = get_list_of_stations()
    trajectory, trajectory_labels = get_otis_trajectory(file, file_labels)
    trajectory_latitude, trajectory_longitude, times_trajectory = interpolate_trajectory(trajectory,100)
  

    trajectories = get_trajectories_year(year=2017)
    print(trajectories)
    plot_map(trajectories, save=True)
    exit()   

    plot_map(trajectory_latitude, trajectory_longitude, save=True)




    #plot_trajectory(trajectory_latitude, trajectory_longitude, times_trajectory, station, save=True)
    
