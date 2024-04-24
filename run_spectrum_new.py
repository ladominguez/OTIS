

new = ['crig', 'moig', 'oxig',  'plig', 'pnig', 'pzig']
components = ['HHZ', 'HHN', 'HHE']

for sta in new:
    for comp in components:
        print(f'python spectrum_parallel.py {sta} {comp}')
        print(f'say -v Mónica "Ya termine {sta} {comp}"')

print('say -v Mónica "Ya termine todo papacito"')