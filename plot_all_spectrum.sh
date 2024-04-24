#!/bin/sh
#
find spectra/ -name "*pkl" | awk '{print "python plot_spectrum.py " $1}'
say -v Mónica 'Ya terminé todo papacito.'
