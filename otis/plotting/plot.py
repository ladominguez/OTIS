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
    cbar.set_label('Spectrum')
   
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
