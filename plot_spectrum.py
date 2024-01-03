from utils import *
import warnings

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)


if __name__ == '__main__':
    input_file = 'spectra/daig/spectrum_daig_HHZ_2023-10-16_00:10:57_2023-10-25_06:38:15.pkl'
    results, config = read_spectrum2file(input_file)
    print_configuration(config)
    plot_spectrum(results, config)
