import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from framework import file_exiobase3
import time


def GWP_element_extractor(flow):
    return flow[:3]

def ISO_code_extractor(flow):
        return flow[:2]

#Control variables
EU28 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
year = 2007
'''
#Reading EXIOBASE file
#start_EXIO_time = time.time()
exio = file_exiobase3.EXIOfiles(EU28, year)
A, Dcba, F, M, Y, x = exio.read()
#end_EXIO_time = time.time() - start_EXIO_time
#print(f'Run time using .pkl files pre-processed: {end_EXIO_time} s')
filt_M = M.loc['GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)']
'''
#Ignite Analysis method
#start_IGNITE_time = time.time()
ig_path = f'C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/exiobase/IOT_{year}_pxp/'
ig_M = pd.read_csv(ig_path + 'impacts/M.txt', sep='\t', low_memory=False)
ig_x = pd.read_csv(ig_path + '/x.txt', sep='\t')
#end_IGNITE_time = time.time() - start_IGNITE_time
#print(f'Run time using ignite analytics´ method: {end_IGNITE_time} s')

#Impacts vector
ig_filt_M = ig_M[ig_M.region.isin(['sector', 'GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)'])].\
        transpose().reset_index()
#ig_filt_M['GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'] = ig_filt_M.astype(float)/1e6
ig_filt_M.columns = ig_filt_M.values[0]
ig_filt_M = ig_filt_M.iloc[1:]
ig_filt_M['region'] = ig_filt_M['region'].apply(ISO_code_extractor)

#filtering GWP stressors from the characterization vectors
GWP_idx = list()
stressor_GWP = ['CO2', 'N2O', 'CH4', 'SF6']
stressor_idx = Dcba.index.tolist()
for i in range(len(stressor_idx)):
        for j in stressor_GWP:
                if stressor_idx[i].find(j) != -1:
                        GWP_idx.append(i)
                        continue

total_stressor = Dcba.iloc[GWP_idx,:]
total_stressor.reset_index(inplace=True)
total_stressor['stressor'] = total_stressor['stressor'].apply(GWP_element_extractor)

#characterization factor (kg CO2 eq)
GW_convert = {'CO2': 1, 'N2O': 298, 'CH4': 25, 'SF6': 22800}
conv_mat = np.zeros((len(total_stressor['stressor']),1))
for stressor in range(np.shape(conv_mat)[0]):
        conv_mat[stressor] = GW_convert[total_stressor['stressor'].values[stressor]]
total_stressor.drop('stressor', axis=1, inplace=True)
total_stressor = total_stressor * conv_mat
#total_stressor = total_stressor.iloc[:13,:]
total_stressor = total_stressor.sum(axis=0)
filt_Dcba = pd.DataFrame(total_stressor)
filt_Dcba.rename(columns={0: "GHG emissions"}, inplace=True)

#Output vector
grouped_x = ig_x.groupby('region')['indout'].transform('sum')
ig_x['total_ISO_output'] = ig_x.groupby('region')['indout'].transform('sum')
ig_x['weighted_sector'] = ig_x['indout'] / grouped_x

#Merging both dataframes
merged_df = ig_filt_M.merge(right=ig_x, how='left', on=['region', 'sector'])
merged_df['weighted GHG emissions [kg CO2 eq/EURO]'] = merged_df['GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)'].astype(float).\
        multiply(merged_df['weighted_sector'], axis='index',)
cols = ['ISO_code', 'Product', 'GHG emissions',
       'Output','total_ISO_output','weight_by_sector', 'Weighted GHG emissions [kg CO2 eq/EURO]']
merged_df.columns = cols


#Huysman 2016
footprint = merged_df[['ISO_code', 'Product','GHG emissions']]
house_occ = np.arange(0,len(Y.columns.values),7)
n_profit_occ = np.arange(1,len(Y.columns.values),7)
Y_cons = Y.iloc[:, house_occ]
Y_n_prof = Y.iloc[:, n_profit_occ]
f = Y @ np.ones((np.shape(Y)[1],1))
f_cons = Y_cons @ np.ones((np.shape(Y_cons)[1],1))
f_cons.columns = ['Total']
footprint['GHG emissions'] = footprint['GHG emissions'].\
                                 astype(float).multiply(f_cons['Total'].values, axis='index')

EU_idx = list()
for ln in range(len(footprint['ISO_code'])):
    if footprint['ISO_code'].values[ln] in EU28:
        EU_idx.append(ln)
footprint = footprint.iloc[EU_idx, :]
EU_sum = footprint['GHG emissions'].sum(axis=0).round(2)/1e12

'''
#EU footprint by activity
path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/conversions/"
conv_HH = np.load(path+'conv_HH.npy')
HH_atv = ['ISO_code','Food', 'Goods', 'Mobility', 'Shelter', 'Services']
EU_footprint = pd.DataFrame(columns=HH_atv)
grouped_frame = footprint.groupby(footprint['ISO_code'])
grp_keys = grouped_frame.groups.keys()
for key in grp_keys:
        curr_group = grouped_frame['GHG emissions'].get_group(key)
        conv_group = np.expand_dims(curr_group, axis=1) * conv_HH
        total_conv = conv_group.sum(axis=0)
        entry = {'ISO_code': key, 'Food': total_conv[0], 'Goods': total_conv[1], 'Mobility': total_conv[2],
                 'Shelter': total_conv[3], 'Services': total_conv[4]}
        EU_footprint.loc[len(EU_footprint)] = entry

EU_footprint.index = EU_footprint['ISO_code']
EU_idx = list()
for ln in range(len(EU_footprint.index)):
    if EU_footprint.index[ln] in EU28:
        EU_idx.append(ln)

EU_footprint = EU_footprint.iloc[EU_idx,:]
footprint_HH = EU_footprint.sum(axis=0)
footprint_HH = footprint_HH.iloc[1:]
footprint_HH /= 1000 #kg to ton
footprint_HH /= 493000000 #per capita


plt.figure()
plt.bar(['w/ services', 'w/o services'], [5.48e12, 5.12e12], width=0.4, color='maroon')
plt.bar(['w/ services', 'w/o services'], [EU_sum, EU_sum_nServs], width=0.2)
plt.legend(['Castellani et al., 2019','file_exiobase3'])
#plt.ylim(0,5)
plt.xlabel('Activity')
plt.ylabel('kg CO2 eq')
plt.title('Global Warming Potential (GWP)')
plt.grid(True)
plt.show()
'''

