

new = ['arig', 'daig', 'caig', 'crig', 'meig', 'moig', 'oxig', 'plig', 'pnig', 'pzig', 'ziig']
new = ['aaig', 'anig', 'ccig', 'cgig', 'cjig', 'cmig', 'csig', 'dhig', 'ftig', 'gtig', 'hlig', 'hpig', 'hsig', 'lnig', 'lpig', 'lvig', 'maig', 'mbig', 'mcig', 'mmig', 'mnig', 'myig', 'pdig', 'peig', 'pnig', 'ppig', 'rpig', 'scig', 'spig', 'srig', 'ssig']
components = ['HHZ', 'HHN', 'HHE']

#new = ['arig']
#components = ['HHZ']

for sta in new:
    for comp in components:
        print(f'python spectrum_parallel.py {sta} {comp}')
    print(f'say -v Mónica "Ya termine {sta} "')

print('say -v Mónica "Ya termine todo papacito"')
