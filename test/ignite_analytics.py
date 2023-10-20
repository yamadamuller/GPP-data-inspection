import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from framework import file_exiobase3
import time


def ISO_code_extractor(flow):
        return flow[:2]

def scale_val(row, category_percentiles, global_upper_limit, global_lower_limit):
    sector = row['region']
    value = row['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)']
    local_lower_limit, local_upper_limit = category_percentiles.loc[category_percentiles['region'] == sector]['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'].values

    if value < 0 and value > -global_upper_limit:
        return [-value]

    if value < global_lower_limit and local_lower_limit < global_lower_limit:
        return [global_lower_limit]
    elif value > global_upper_limit and local_upper_limit > global_upper_limit:
        return [global_upper_limit]

    if value < local_lower_limit and not local_lower_limit == 0:
        return [local_lower_limit]
    elif value > local_upper_limit:
        return [local_upper_limit]
    elif value == 0 or value == np.nan:
        return [global_lower_limit]

    return value

#Control variables
EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
year = 2007

#Reading EXIOBASE file
start_EXIO_time = time.time()
exio = file_exiobase3.EXIOfiles(EU27, year)
A, Dcba, F, M, Y, x = exio.read()
end_EXIO_time = time.time() - start_EXIO_time
print(f'Run time using .pkl files pre-processed: {end_EXIO_time} s')
filt_M = M.loc['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)']

#Ignite Analysis method
start_IGNITE_time = time.time()
ig_path = f'C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/exiobase/IOT_{year}_pxp/'
ig_M = pd.read_csv(ig_path + 'impacts/M.txt', sep='\t', low_memory=False)
ig_x = pd.read_csv(ig_path + '/x.txt', sep='\t')
end_IGNITE_time = time.time() - start_IGNITE_time
print(f'Run time using ignite analytics´ method: {end_IGNITE_time} s')

#Impacts vector
ig_filt_M = ig_M[ig_M.region.isin(['sector','GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'])].\
        transpose().reset_index()
#ig_filt_M['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'] = ig_filt_M.astype(float)/1e6
ig_filt_M.columns = ig_filt_M.values[0]
ig_filt_M = ig_filt_M.iloc[1:]
ig_filt_M['region'] = ig_filt_M['region'].apply(ISO_code_extractor)


# limit outliers
ig_filt_M['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'] = ig_filt_M['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'].astype(float)
global_lower_limit, global_upper_limit = ig_filt_M['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'].replace(0, np.nan).quantile([0.03, 0.97]).values
category_percentiles = ig_filt_M.replace(0, np.nan).groupby('region')['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'].quantile([0.05, 0.95]).reset_index()
ig_filt_M['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'] = ig_filt_M[['region','GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)']].apply(
        lambda row: scale_val(row, category_percentiles, global_upper_limit, global_lower_limit), axis=1,
        result_type='expand').values


#Output vector
grouped_x = ig_x.groupby('region')['indout'].transform('sum')
ig_x['total_ISO_output'] = ig_x.groupby('region')['indout'].transform('sum')
ig_x['weighted_sector'] = ig_x['indout'] / grouped_x

#Merging both dataframes
merged_df = ig_filt_M.merge(right=ig_x, how='left', on=['region', 'sector'])
merged_df['weighted GHG emissions [kg CO2 eq/EURO]'] = merged_df['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'].\
        astype(float).multiply(merged_df['weighted_sector'], axis='index',)
cols = ['ISO_code', 'Product', 'GHG emissions AR5 (GWP100)',
         'Output','total_ISO_output','weight_by_sector', 'Weighted GHG emissions [kg CO2 eq/EURO]']
merged_df.columns = cols


#Huysman 2016
footprint = merged_df[['ISO_code', 'Product','GHG emissions AR5 (GWP100)']]
#house_occ = np.arange(0,len(Y.columns.values),7)
#Y = Y.iloc[:, house_occ]
f = Y @ np.ones((np.shape(Y)[1],1))
f.columns = ['Total']
footprint['GHG emissions AR5 (GWP100)'] = footprint['GHG emissions AR5 (GWP100)'].\
                                    astype(float).multiply(f['Total'].values, axis='index')

#EU footprint by activity
path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/conversions/"
conv_HH = np.load(path+'conv_HH.npy')
HH_atv = ['ISO_code','Food', 'Goods', 'Mobility', 'Shelter', 'Services']
EU_footprint = pd.DataFrame(columns=HH_atv)
grouped_frame = footprint.groupby(footprint['ISO_code'])
grp_keys = grouped_frame.groups.keys()
for key in grp_keys:
        curr_group = grouped_frame['GHG emissions AR5 (GWP100)'].get_group(key)
        conv_group = np.expand_dims(curr_group, axis=1) * conv_HH
        total_conv = conv_group.sum(axis=0)
        entry = {'ISO_code': key, 'Food': total_conv[0], 'Goods': total_conv[1], 'Mobility': total_conv[2],
                 'Shelter': total_conv[3], 'Services': total_conv[4]}
        EU_footprint.loc[len(EU_footprint)] = entry

EU_footprint.index = EU_footprint['ISO_code']
EU_idx = list()
for ln in range(len(EU_footprint.index)):
    if EU_footprint.index[ln] in EU27:
        EU_idx.append(ln)

EU_footprint = EU_footprint.iloc[EU_idx,:]
footprint_HH = EU_footprint.sum(axis=0)
footprint_HH = footprint_HH.iloc[1:]
#footprint_HH /= 1000 #kg to ton
#footprint_HH /= 493000000 #per capita

#Castellani2019
EU_sum = footprint_HH.sum(axis=0)/1e12
EU_sum_nServs = footprint_HH.iloc[:-1].sum(axis=0)/1e12

plt.figure()
plt.bar(footprint_HH.index, footprint_HH.values, width=0.4)
plt.ylim(0,5)
plt.xlabel('Activity')
plt.ylabel('tons CO2 eq per capita')
plt.title('Global Warming Potential (GWP)')
plt.grid(True)
plt.show()
