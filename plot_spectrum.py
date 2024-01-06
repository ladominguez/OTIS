from utils import *
import warnings

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)


if __name__ == '__main__':
    input_file = 'spectra/caig/spectrum_caig_HHZ_2023-10-16_03:50:17_2023-10-26_23:58:32.pkl'
    results, config = read_spectrum2file(input_file)
    mean_spectrum = get_average_spectrum(results, 0, 2)
    t0 = get_time_from_index(results, 20)
    t1 = get_time_from_index(results, 40)
    #print_configuration(config)
    #fig, ax = plot_spectrum(results, config, plot_fig = False)
    #fig, ax = plot_average_box(fig, ax, t0, t1, color = 'green')
    spectrogram = get_average_spectrum(results, 20, 40)
    plt.show()