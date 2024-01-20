from utils import *
import warnings

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)


if __name__ == '__main__':
    input_file = 'spectra/caig/spectrum_caig_HHZ_2023-10-16_03:50:17_2023-10-26_23:58:32.pkl'
    results, config = read_spectrum2file(input_file)
    station = config['station']['name']
    component = config['station']['component']
    index1 = 20
    index2 = 40
    t0 = get_time_from_index(results, index1)
    t1 = get_time_from_index(results, index2)
    results_demeaned = remove_average_spectrum(results, index1, index2)
    #spectrogram = get_average_spectrum(results, index1, index2)
    print_configuration(config)
    fig, ax = plot_spectrum(results_demeaned, config, plot_fig = True, demean_plot=True)
    save_figure(fig, station, component)
    #fig, ax = plot_average_box(fig, ax, t0, t1, color = 'green')
    #plt.show()