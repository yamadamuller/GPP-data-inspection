import numpy as np
import pandas as pd

from framework import file_exiobase3

EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']

year = 2007
exio = file_exiobase3.EXIOfiles(EU27, year, region_filter=True)
M, Y, Z = exio.read()

#basket-of-products
path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/conversions/"
conv_HH = np.load(path+'conv_HH.npy')
HH_atv = ['Food', 'Goods', 'Mobility', 'Shelter', 'Services']
EU_basket = pd.DataFrame(columns = HH_atv)
reg_count = 0
for reg in EU27[0:1]:
        curr_Z = Z[reg]
        sum_Z = curr_Z.sum(axis=0).to_frame().T

