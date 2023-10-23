import numpy as np
import pandas as pd
from framework import file_exiobase3

def GWP_element_extractor(flow):
    return flow[:3]

def ISO_code_extractor(flow):
        return flow[:2]

#Control variables
EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
year = 2007

exio = file_exiobase3.EXIOfiles(EU27, year)
fA, fDcba, fF, fM, fY, fx = exio.read()

#Ignite Analysis method
ig_path = f'C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/exiobase/IOT_{year}_pxp/'
Dcba = pd.read_csv(ig_path + 'impacts/D_cba.txt', sep='\t', low_memory=False)
x = pd.read_csv(ig_path + '/x.txt', sep='\t')
Y = pd.read_csv(ig_path + '/Y.txt', sep='\t', low_memory=False)
sDcba = pd.read_csv(ig_path + 'satellite/D_cba.txt', sep='\t', low_memory=False)

#Impacts vector
filt_Dcba = Dcba[Dcba.region.isin(['sector', 'GHG emissions (GWP100) | Problem oriented approach: baseline (CML, 2001) | GWP100 (IPCC, 2007)'])].\
        transpose().reset_index()
filt_Dcba.columns = filt_Dcba.values[0]
filt_Dcba= filt_Dcba.iloc[1:]
filt_Dcba['region'] = filt_Dcba['region'].apply(ISO_code_extractor)
filt_Dcba.columns = ['region', 'product', 'GHG emissions']
#Output vector
grouped_x = x.groupby('region')['indout'].transform('sum')
x['total_ISO_output'] = x.groupby('region')['indout'].transform('sum')

#Demand matrix
Y.columns = Y.values[0]
Y = Y.iloc[2:,:]
Y.rename(columns={'category': "ISO_code", 'nan': 'Product'}, inplace=True)
f = Y.iloc[:,2:].astype(float) @ np.ones((np.shape(Y.iloc[:,2:])[1],1))
inv_f = 1/f
idx_inf = np.where(inv_f == np.inf)[0]
inv_f.iloc[idx_inf,:] = 0
inv_f.rename(columns={0: 'Demand'}, inplace=True)

#Huysman 2016
footprint = filt_Dcba
footprint['GHG emissions/Euro'] = footprint['GHG emissions'].\
                                 astype(float).multiply(inv_f['Demand'].values, axis='index')

hh_demand = Y.iloc[:,np.where(Y.columns == 'Final consumption expenditure by households')[0]]
hh_demand = hh_demand.astype(float).sum(axis=1)
hh_demand = pd.DataFrame(hh_demand)
hh_demand.rename(columns={0: 'Household demand'}, inplace=True)
footprint['Household GHG emissions'] = footprint['GHG emissions/Euro'].\
                                 astype(float).multiply(hh_demand['Household demand'].values, axis='index')

EU_idx = list()
for ln in range(len(footprint['region'])):
    if footprint['region'].values[ln] in EU27:
        EU_idx.append(ln)
footprint = footprint.iloc[EU_idx, :]

grouped_hh = footprint.groupby('region')['Household GHG emissions'].transform('sum')
ISO_occ = np.arange(0, len(grouped_hh), 200)
grouped_hh = grouped_hh.iloc[ISO_occ]
grouped_hh.index = EU27
EU_sum = grouped_hh.sum(axis=0)/1e12

#filtering GWP stressors from the characterization vectors
GWP_idx = list()
stressor_GWP = ['CO2', 'N2O', 'CH4', 'SF6']
stressor_idx = fDcba.index.tolist()
for i in range(len(stressor_idx)):
        for j in stressor_GWP:
                if stressor_idx[i].find(j) != -1:
                        GWP_idx.append(i)
                        continue

total_stressor = fDcba.iloc[GWP_idx,:]
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
filt_fDcba = pd.DataFrame(total_stressor)
filt_fDcba.rename(columns={0: "GHG emissions"}, inplace=True)

test = filt_fDcba
test['GHG emissions/Euro'] = test['GHG emissions'].\
                                 astype(float).multiply(inv_f['Demand'].values, axis='index')
test['Household GHG emissions'] = test['GHG emissions/Euro'].\
                                 astype(float).multiply(hh_demand['Household demand'].values, axis='index')

test = test.iloc[EU_idx, :]
test.reset_index(inplace=True)
test_hh = footprint.groupby('region')['Household GHG emissions'].transform('sum')
ISO_occ = np.arange(0, len(grouped_hh), 200)
grouped_hh = grouped_hh.iloc[ISO_occ]
grouped_hh.index = EU27
EU_sum = grouped_hh.sum(axis=0)/1e12
