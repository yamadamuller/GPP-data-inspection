import numpy as np
from framework import file_exiobase3

'''
- Paper: Assessing the environmental impacts of EU consumption at macro-scale (Antoine Beylot, 2019)
- DOI: https://doi.org/10.1016/j.jclepro.2019.01.134
- Data: Exiobase 3 2011 ixi
- Data pre-proc: (Household + Governmental + Non-profit) consumption + integrated investments
- GHG emissions account for CO2, N20, CH4, PFC, HFC, SF6, CF4 
  (it is advised to update the gwp_filter() function)
- Output: (Total EU28 Climate Change Footprint in kg CO2 eq) / 1e12
'''

#Control variables
EU28 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
year = 2010

#Running the IO-model
Beylot = file_exiobase3.EXIOfiles(EU28, year, analysis='industry')
Beylot.read()
EU28_footprint = Beylot.emission_estimator(AR5=False)
output = np.round(1000*EU28_footprint.sum(axis=0) / 1e12, 2)
print(f"IO-Consumer Footprint = {output}E+12 kg CO2 eq")
dir_acc = Beylot.direct_emissions_valid().sum(axis=0) / 1e12
new_dir_percentage = 100*dir_acc/output
