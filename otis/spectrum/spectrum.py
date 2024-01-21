from mtspec import mtspec
from tqdm import tqdm
import numpy as np
import pickle
from obspy.core import read


def load_configuration(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

def print_configuration(config):
    for section in config.sections():
        print(f"[{section}]")
        for key in config[section]:
            print(f"{key} = {config[section][key]}")
        print()