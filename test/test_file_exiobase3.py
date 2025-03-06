from framework import file_exiobase3

#Control variables
EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
year = 2010

#Class test
test = file_exiobase3.EXIOfiles(EU27, year, analysis='product', type_cons='household')
test.read()
sfp = test.emission_estimator(per_capita=True)



