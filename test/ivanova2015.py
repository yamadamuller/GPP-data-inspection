from framework import file_exiobase3

'''
- Paper: Environmental Impact Assessment of Household Consumption (Diana Ivanova, 2015)
- DOI: https://doi.org/10.1111/jiec.12371
- Data: Exiobase 3 2007 pxp
- Data pre-proc: Household consumption + integrated investments + changes in inventories and valuables
- Output: GHG emissions in kg CO2 eq for a list of regions
- OBS: given that the paper uses reference year of 2007, it is advised to chance from
GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010) to 
GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007) in the read() 
function of the file_exiobase3.py
'''

from framework import file_exiobase3

#Control variables
EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
year = 2007

#Class test
test = file_exiobase3.EXIOfiles(EU27, year, analysis='product', type_cons='household')
test.read()
sfp = 1000*test.emission_estimator()
dir_acc = test.direct_emissions_valid()
new_dir_percentage = 100*dir_acc/sfp