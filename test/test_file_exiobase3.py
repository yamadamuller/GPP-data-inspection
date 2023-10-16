import numpy as np
from framework import file_exiobase3

#Control variables
EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
EU_pop = 493000000
year = 2007

#Reading EXIOBASE file
exio = file_exiobase3.EXIOfiles(EU27, year, region_filter=True, household=True)
A, Dcba, F, M, S, Y, Z = exio.read()









