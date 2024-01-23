from  otis import spectrum
from otis import core
import warnings

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)


if __name__ == '__main__':
    config = core.load_configuration('configuration.ini')
    core.print_configuration(config)
    results = spectrum.get_spectrum_parallel_processing(config, cores=8)
    core.save_spectrum2file(results,config) 

            