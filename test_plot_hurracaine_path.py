import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygmt
import ssn

# Create a DataFrame
file = 'hurracaine_path.dat'

df = pd.read_csv(file, delim_whitespace=True, names=['datetime', 'lat', 'lon'], dtype = {'datetime': str, 'lat': float, 'lon': float})
df['datetime'] = pd.to_datetime(df['datetime'], format='%Y/%m/%dT%H:%M:%S')
print(df.head())


if __name__ == '__main__':
    # Create a figure and an axis
    fig = pygmt.Figure()
    ssn_stations = ssn.get_all_stations()

    # Set the region and projection
    region = "-120/-80/10/30"
    projection = "M8i"
    frame= ['WSne','xa4f2','ya2f2']
    fig.basemap(region=region, projection=projection, frame=frame)

    # Plot the map of Mexico
    fig.coast(land="gray", water="skyblue", shorelines=True)
    fig.plot(x=df['lon'], y=df['lat'], style='c0.1c', fill='red', pen='black')

    for row in ssn_stations.itertuples():
        fig.plot(x=row.longitude, y=row.latitude, style='t0.3c', pen='1p', fill='white', label=row.stnm)

    # Show the plot
    fig.show()