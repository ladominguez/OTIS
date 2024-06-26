from  otis import spectrum
from otis import core
import warnings
import sys

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)


if __name__ == '__main__':

    config = core.load_configuration('configuration.ini')
    core.print_configuration(config)
    print('+============================+')
    print('| Running spectrum_parallel.py |')
    print('+============================+')
    print('type: {}'.format(type(config)))
    if len(sys.argv) > 1:
        station = sys.argv[1]
        component = sys.argv[2]
        config.set('station', 'name', station)
        config.set('station', 'component', component)
    
    core.print_configuration(config)
    results = spectrum.get_spectrum_parallel_processing(config, cores=8)
    core.save_spectrum2file(results,config) 

            