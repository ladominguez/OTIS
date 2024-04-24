from otis import core
from otis import tools
from otis.plotting import plot, tools
import pycpt

import warnings
import sys

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)
demean_plot = False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide input file as argument')
        input_file = 'spectra/caig/spectrum_caig_HHZ_2023-10-16_03:50:17_2023-10-26_23:58:32.pkl'
        #sys.exit(1)
    else:
        input_file = sys.argv[1]
    cpt = pycpt.load.gmtColormap('./cpt/BlueWhiteOrangeRed.cpt')
    #input_file = sys.argv[1]
    results, config = core.read_spectrum2file(input_file)
    station = config['station']['name']
    component = config['station']['component']
    index1 = 20
    index2 = 240
    t0 = core.get_time_from_index(results, index1)
    t1 = core.get_time_from_index(results, index2)
    results_demeaned = tools.remove_average_spectrum(results, index1, index2)
    core.print_configuration(config)

    if demean_plot:
        fig, ax = plot.plot_spectrum(results_demeaned, config, plot_fig = False, demean_plot=demean_plot)
        fig, ax = plot.plot_average_box(fig, ax, t0, t1, color='black')
    else:
        fig, ax = plot.plot_spectrum(results, config, plot_fig = False, demean_plot=demean_plot)

    fig, ax = plot.plot_touchdown(fig, ax, core.get_touchdown_time(), color='blue')
    fig, ax = plot.plot_line_at_period(fig, ax, 3, color='red')

    plot.save_figure(fig, station, component)


    #fig, ax = plot_average_box(fig, ax, t0, t1, color = 'green')
    #plt.show()
