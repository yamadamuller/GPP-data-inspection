import numpy as np
from framework import file_exiobase3

EU27 = ['AT', 'BE', 'BG', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU', 'IE', 'IT',
        'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']

year = 2007
exio = file_exiobase3.EXIOfiles(EU27, year, region_filter=True)
M, Y, Z = exio.read()








