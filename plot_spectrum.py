from utils import *
import warnings

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)


if __name__ == '__main__':
    input_file = 'spectra/caig/spectrum_caig_HHZ_2023-10-16_03:50:17_2023-10-26_23:58:32.pkl'
    results, config = read_spectrum2file(input_file)
    mean_spectrum = get_average_spectrum(results[0][1], 0, 10)
    #print_configuration(config)
    #plot_spectrum(results, config)
