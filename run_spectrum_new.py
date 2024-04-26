

new = ['arig', 'daig', 'caig', 'crig', 'meig', 'moig', 'oxig', 'plig', 'pnig', 'pzig', 'ziig']
new = ['caig']
components = ['HHZ', 'HHN', 'HHE']

#new = ['arig']
#components = ['HHZ']

for sta in new:
    for comp in components:
        print(f'python spectrum_parallel.py {sta} {comp}')
    print(f'say -v Mónica "Ya termine {sta} "')

print('say -v Mónica "Ya termine todo papacito"')
