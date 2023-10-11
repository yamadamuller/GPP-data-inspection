import numpy as np
import pandas as pd

from framework import file_exiobase3

EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']

year = 2007
exio = file_exiobase3.EXIOfiles(EU27, year, region_filter=True)
M, Y, A = exio.read()

#basket-of-products
path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/conversions/"
conv_HH = np.load(path+'conv_HH.npy')
HH_atv = ['ISO_code','Food', 'Goods', 'Mobility', 'Shelter', 'Services']
EU_basket = pd.DataFrame(columns = HH_atv)
for reg in EU27:
        curr_A = A[reg]
        sum_A = curr_A.sum(axis=0).to_frame()
        conv_A = sum_A.values * conv_HH
        total_conv = conv_A.sum(axis=0)
        entry = {'ISO_code': reg,'Food': total_conv[0],'Goods': total_conv[1], 'Mobility': total_conv[2],
                 'Shelter': total_conv[3], 'Services': total_conv[4]}
        EU_basket.loc[len(EU_basket)] = entry

#filtering GWP stressors from the characterization vectors
test = M.index.tolist()

#IO-model calculations
f = Y @ np.ones((np.shape(Y)[1],1))
output = np.linalg.inv(np.eye(len(A)) - A) @ f
