import numpy as np
import os
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FixedLocator
from datetime import datetime
from otis.plotting.tools import get_spectrum_from_results
from otis import core




GRDDIR='/Users/antonio/Dropbox/MEXICO_GRD/Mexico_All'
trench_file = '/Users/antonio/Dropbox/gmt/trench.gmt'
iso_line_20km = '/Users/antonio/Dropbox/Slab2.0/isoline20.txt'
iso_line_40km = '/Users/antonio/Dropbox/Slab2.0/isoline40.txt'
iso_line_60km = '/Users/antonio/Dropbox/Slab2.0/isoline60.txt'
iso_line_80km = '/Users/antonio/Dropbox/Slab2.0/isoline80.txt'
iso_line_100km = '/Users/antonio/Dropbox/Slab2.0/isoline100.txt'
iso_line_120km = '/Users/antonio/Dropbox/Slab2.0/isoline120.txt'
CPTFILE='/Users/antonio/Dropbox/BSL/CRSMEX/Presentations/SSA_meeting_2024/map_repeaters/wikifrance_mexico.cpt'

figure_size = (12, 3)

def plot_spectrum(results, config, plot_fig=True, demean_plot=False):
    """
    Plot the spectrum of seismic data.

    Args:
        results (list): List of tuples containing the results of the spectrum analysis.
            Each tuple should have the format (time, spectrum, period).
        config (dict): Configuration settings for the plot.
            It should contain the keys 'station' and 'spectrum'.
        plot_fig (bool, optional): Whether to display the plot. Defaults to True.

    Returns:
        tuple: A tuple containing the figure and axis objects of the plot.

    """
    times = [result[0] for result in results]
    if demean_plot:
        spectra = get_spectrum_from_results(results)
    else:
        spectra = [np.clip(result[1], -15, None) for result in results]
        #spectra = [result[1] for result in results]
    periods = [result[2] for result in results]
    Aspec_max = max(max(spec) for spec in spectra)
    # The next 3 lines remove the -inf values from the spectra, and then calculate the minimum value
    Aspec_min = np.min(spectra, axis = 1)
    Aspec_min_no_inf = np.where(Aspec_min == -np.inf, np.nan, Aspec_min)
    Aspec_min = np.nanmin(Aspec_min_no_inf, axis = 0)

    station = config['station']['name']
    component = config['station']['component']
    T_min = eval(config['spectrum']['T_min'], {'__builtins__': None}, {})
    T_max = eval(config['spectrum']['T_max'], {'__builtins__': None}, {})

    # create a spectrogram plot using matplotlib
    fig, ax = plt.subplots(figsize=figure_size)
    ax.set_title(station.upper() + ' - ' + component)
    ax.set_xlabel('Time')
    ax.set_ylabel('Period')
    ax.set_yscale('log')
    ax.set_ylim(T_min, T_max)
    ax.set_xlim(min(times).datetime, max(times).datetime)
    ax.set_facecolor('black')
    xticks = ax.get_xticks()
    ax.xaxis.set_major_locator(FixedLocator(xticks))
    ax.set_xticklabels(xticks, rotation=45)

    date_form = DateFormatter("%Y-%b-%d")
    ax.xaxis.set_major_formatter(date_form)

    for ti, period, spectrum in zip(times, periods, spectra):
        t = [ti.datetime for _ in range(len(period))]
        if demean_plot:
            Aspec_max_abs = max(abs(Aspec_max), abs(Aspec_min))
            ax.scatter(t, period, c=spectrum, cmap='seismic', vmin=-Aspec_max_abs, vmax=Aspec_max_abs, s=12, marker='s')
        else:
            ax.scatter(t, period, c=spectrum, cmap='hot', vmin=Aspec_min, vmax=Aspec_max, s=12, marker='s')
            
    cbar = plt.colorbar(ax.collections[0], ax=ax, orientation='vertical')
    cbar.set_label(r'Amplitud $[m^2/s^4/Hz] [dB]$')
   
    if plot_fig:
        plt.show()

    return fig, ax

def plot_average_box(fig, ax, t0, t1, color='white'):
    # make the outline of the box black
    ax.axvspan(t0.datetime, t1.datetime, linewidth=3,
               edgecolor=color, facecolor='none', clip_on=True)
    #ax.axvspan(t0.datetime, t1.datetime, linewidth=3)
    return fig, ax

def plot_hurracaine_stages(fig, ax):
    ax.axvspan(datetime(2023,10,23,3,0), datetime(2023,10,24,9,0), color='green', alpha=0.35) # Tropical storm 
    ax.axvspan(datetime(2023,10,24,9,0), datetime(2023,10,24,19,0), color='orange', alpha=0.35)
    ax.axvspan(datetime(2023,10,24,19,0), datetime(2023,10,25,6,0), color='purple', alpha=0.35)
    ax.axvspan(datetime(2023,10,25,6,0), datetime(2023,10,25,15,0), color='orange', alpha=0.35)
    ax.axvspan(datetime(2023,10,25,15,0), datetime(2023,10,25,21,0), color='green', alpha=0.35)
    return fig, ax

def plot_map(quick=True, isolines=False, closeup = True, tmvb=False):
    import pygmt
    fig = pygmt.Figure()
    if closeup:
        region = "-108/-90/14/31.5"
    else:
        region = "-108/-90/10/21.5"

    projection = "M8i"
    frame= ['WSne','xa4f2','ya2f2']
    fig.basemap(region=region, projection=projection, frame=frame)

    if not quick:
        print('Working on grid')
        fig.grdimage(grid=GRDDIR+'/MEXICO_ALL.nc', shading=GRDDIR+'/MEXICO_ALLi.nc', cmap=CPTFILE,frame=True)
        print('finished grid')

    fig.coast(water="lightblue", shorelines=True, map_scale="jBL+w500k+o0.5c/0.5c+f+u")
    fig.plot(data = trench_file, style="f0.5i/0.10i+l+t", pen="1p,black", fill='gray50')
    #fig.plot(x=-107.6, y=16.60, fill='red',style='c0.35c', pen='2p,black')

    if isolines:
        fig.plot(data = iso_line_20km, pen="0.75p,black,--", transparency=50)
        fig.plot(data = iso_line_40km, pen="0.75p,black,--", transparency=50)
        fig.plot(data = iso_line_80km, pen="0.75p,black,--", transparency=50)
        fig.plot(data = iso_line_100km, pen="0.75p,black,--", transparency=50)
        fig.plot(data = iso_line_120km, pen="0.75p,black,--", transparency=50)
    
    if tmvb:
        fig.plot(data='/Users/antonio/Dropbox/gmt/tecto/tmvb.d',pen ="1p,black", close=True, transparency=50, fill='gray75')


    return fig


def plot_line_at_period(fig, ax, T0, color='black'):
    ax.axhline(y=T0, color=color, linestyle='--')
    return fig, ax

def plot_touchdown(fig, ax, t0, color='black'):
    ax.axvline(x=t0, color=color, linestyle='--')
    return fig, ax

def save_figure(fig, station, component, resolution=300, demean_plot=False):

    file_figure = '_'.join(['spectrum', station, component]) + '.png'
                            #datetime.utcfromtimestamp(min(times)).strftime('%Y-%m-%d_%H:%M:%S'),
                            #datetime.utcfromtimestamp(max(times)).strftime('%Y-%m-%d_%H:%M:%S')]) + '.png'
    file_figure = os.path.join('figures',file_figure)
    if demean_plot:
        file_figure = file_figure.replace('.png', '_demean.png')
    
    print('Saving figure to: ', file_figure)
    fig.savefig(file_figure, dpi=resolution, bbox_inches='tight')
