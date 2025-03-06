import numpy as np
from framework import file_exiobase3

'''
- Paper: Environmental impacts of household consumption in Europe: Comparing process-based LCA and 
environmentally extended input-output analysis (Valentina Castellani, 2019)
- DOI: https://doi.org/10.1016/j.jclepro.2019.117966
- Data: Exiobase 3 2011 pxp
- Data pre-proc: Household consumption + integrated investments
- Output: (Total EU28 Climate Change Footprint in kg CO2 eq) / 1e12
'''

#Control variables
EU28 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
year = 2011

#Running the IO-model
Castellani = file_exiobase3.EXIOfiles(EU28, year, analysis='product', type_cons='household')
Castellani.read()
EU28_footprint = Castellani.emission_estimator()
output = np.round(1000*EU28_footprint.sum(axis=0) / 1e12, 2)
print(f"IO-Consumer Footprint = {output}E+12 kg CO2 eq")

