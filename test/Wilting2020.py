from framework import file_exiobase3

'''
- Paper: Subnational greenhouse gas and land-based biodiversity footprints in the European Union 
(Harry C. Wilting, 2020)
- DOI:  https://doi.org/10.1111/jiec.13042
- Data: Exiobase 3 2010 pxp
- Data pre-proc: (Household + Governmental + Non-profit) consumption + integrated investments
- GHG emissions account only CO2, N20 and CH4
- Output: GHG emissions in ton CO2 eq for a list of regions
- OBS: the validation takes into account the minimum and maximum values yielded for the countries
'''

#Control variables
EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
year = 2010

#Running the IO-model
Wilting = file_exiobase3.EXIOfiles(EU27, year, analysis='product')
Wilting.read()
EU27_footprint = Wilting.emission_estimator(AR5=False, per_capita=True)
cols_to_filter = ['AT', 'BE', 'CZ', 'DE', 'DK', 'ES', 'FI', 'FR',
                  'GR', 'HU', 'IE', 'IT', 'PL', 'PT', 'SK', 'GB']
EU27_footprint = EU27_footprint[cols_to_filter]
