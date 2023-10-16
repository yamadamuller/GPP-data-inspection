import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from framework import file_exiobase3

def GWP_element_extractor(flow):
        return flow[:3]

#Control variables
EU27 = ['AT', 'BE', 'BG', 'CZ', 'CY', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HU',
        'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'GB']
EU_pop = 493000000
year = 2007
idx_stress = 13

#Reading EXIOBASE file
exio = file_exiobase3.EXIOfiles(EU27, year, region_filter=True, household=True)
A, Dcba, F, M, S, Y, Z = exio.read()
test = Y

#IO-model calculations (Leontief)
house_occ = np.arange(0,len(Y.columns.values),7)
Y = Y.iloc[:, house_occ]
f = Y @ np.ones((np.shape(Y)[1],1))
L = np.linalg.inv(np.eye(len(A)) - A)
output = L @ f
output.rename(columns={0: "output"}, inplace=True)
output.index = f.index
reg = list()
for idx in range(len(f.index)):
        reg.append(f.index[idx][0])
output['ISO_code'] = reg
#output.rename(columns={0: "output"}, inplace=True)

#filtering GWP stressors from the characterization vectors
GWP_idx = list()
stressor_GWP = ['CO2', 'N2O', 'CH4', 'SF6']
stressor_idx = F.index.tolist()
for i in range(len(stressor_idx)):
        for j in stressor_GWP:
                if stressor_idx[i].find(j) != -1:
                        GWP_idx.append(i)
                        continue

total_stressor = F.iloc[GWP_idx,:]
total_stressor.reset_index(inplace=True)
total_stressor['stressor'] = total_stressor['stressor'].apply(GWP_element_extractor)

#characterization factor (kg CO2 eq)
GW_convert = {'CO2': 1, 'N2O': 298, 'CH4': 25, 'SF6': 22800}
conv_mat = np.zeros((len(total_stressor['stressor']),1))
for stressor in range(np.shape(conv_mat)[0]):
        conv_mat[stressor] = GW_convert[total_stressor['stressor'].values[stressor]]
total_stressor.drop('stressor', axis=1, inplace=True)
total_stressor = total_stressor * conv_mat

#Testing household accounting
f_hh = test @ np.ones((np.shape(test)[1],1))
total_req = M @ np.diagflat(f_hh)
invMat = Dcba - total_req.values
conv_invMat = invMat.iloc[GWP_idx,:]
conv_invMat = conv_invMat * conv_mat
conv_invMat = conv_invMat.iloc[:idx_stress,:]
sum_invMat = conv_invMat.sum(axis=0)

#Environmental matrix
x_hat = np.diagflat(1/output['output'])
x_hat[np.where(x_hat == np.inf)] = 0
B = total_stressor.iloc[:idx_stress,:] @ x_hat

#Inventory vector
g = B @ L
g = g.sum(axis=0)
footprint = g @ np.diagflat(f) + sum_invMat
footprint /= EU_pop
footprint = pd.DataFrame(footprint)
footprint.index = A.index

#footprint
path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/conversions/"
conv_HH = np.load(path+'conv_HH.npy')
HH_atv = ['ISO_code','Food', 'Goods', 'Mobility', 'Shelter', 'Services']
EU_footprint = pd.DataFrame(columns=HH_atv)
footprint.index = A.index
reg = list()
for idx in range(len(footprint.index)):
        reg.append(footprint.index[idx][0])
footprint['ISO_code'] = reg
footprint.rename(columns={0: "output"}, inplace=True)
grouped_frame = footprint.groupby(footprint['ISO_code'])
grp_keys = grouped_frame.groups.keys()
for key in grp_keys:
        curr_group = grouped_frame['output'].get_group(key)
        conv_group = np.expand_dims(curr_group, axis=1) * conv_HH
        total_conv = conv_group.sum(axis=0)
        entry = {'ISO_code': key, 'Food': total_conv[0], 'Goods': total_conv[1], 'Mobility': total_conv[2],
                 'Shelter': total_conv[3], 'Services': total_conv[4]}
        EU_footprint.loc[len(EU_footprint)] = entry

footprint_HH = EU_footprint.sum(axis=0)
footprint_HH = footprint_HH.iloc[1:]
footprint_HH /= 1000

plt.figure()
plt.bar(footprint_HH.index, footprint_HH.values, width=0.4)
plt.xlabel('Activity')
plt.ylabel('tons CO2 eq per capita')
plt.title('Global Warming Potential (GWP)')
plt.show()
