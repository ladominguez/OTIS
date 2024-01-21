from  otis import spectrum
import warnings

# Ignore all instances of RuntimeWarning
warnings.filterwarnings('ignore', category=RuntimeWarning)


if __name__ == '__main__':
    config = spectrum.load_configuration('configuration.ini')
    #results = get_spectrum_parallel_processing(config, cores=8)
    #save_spectrum2file(results,config) 

            