import json
import os
import pandas as pd
from framework import file_basegov, file_exiobase3

#Control variables
year = 2017
ISO_code = 'PT'
contract_ID = list()
absolute_path = os.path.abspath('..')

#Reading the basegov and exiobase 3 files
basegov_data = file_basegov.BASEGOVfiles(years=year)
fill_entries = basegov_data.read()
exio3_data = file_exiobase3.EXIOfiles(ISO_code, year, analysis='industry', type_cons='government')
exio3_data.read()
exio3_fp = 1000*exio3_data.emission_estimator()

#Importing the CPV to Exiobase industry dictionary
dict_path = os.path.join(absolute_path, "data/conversions/CPV_NACE/cpv_exio_dict.json")
with open(dict_path, 'r') as json_file:
    exio_dict = json.load(json_file)

#Importing the CPV to NACE industry dictionary
dict_path = os.path.join(absolute_path, "data/conversions/CPV_NACE/cpv_cpa_dict.json")
with open(dict_path, 'r') as json_file:
    nace_dict = json.load(json_file)

#Importing the NACE to EXIOBASE industry dictionary
dict_path = os.path.join(absolute_path, "data/conversions/CPV_NACE/nace_exio_dict.json")
with open(dict_path, 'r') as json_file:
    cpv_dict = json.load(json_file)

#Searching for contracts involving public procurement of school cafeterias
occ_cafet = fill_entries['objectoContrato'].str.contains('extracao de miner').fillna(False)
fill_entries = fill_entries[occ_cafet]

#Populating the contract_ID list
for ID in fill_entries.index:
    contract_ID.append(ID)
if isinstance(contract_ID, list):
    contract_ID = contract_ID
else:
    contract_ID = [contract_ID]

#Creating the dataframe containing the emission data for the contract
exio3_data.filt_AR5.index = exio3_data.filt_AR5['region']
exio3_data.filt_AR5.drop('region', axis=1, inplace=True)
cols = ['idcontrato', 'objectoContrato', 'cpv', 'dataCelebracaoContrato',
        'precoContratual', 'kg Co2 eq', 'percentage of total emissions (%)']
public_report = pd.DataFrame(columns=cols)
for c_ID in contract_ID:
    #ID based info
    curr_cont = fill_entries.loc[c_ID]
    seller_ISO = 'PT'
    nace_cat = nace_dict[curr_cont['cpv']][0]
    # NACE based footprints
    total_idx = exio3_data.footprint['product'].isin(cpv_dict[nace_cat])
    ind_idx = exio3_data.footprint['product'].str.contains(exio_dict[curr_cont['cpv']])
    total_nace_fp = exio3_data.footprint[total_idx]
    ind_fp = exio3_data.footprint[ind_idx]
    total_nace_fp = total_nace_fp.sum(axis=0)
    emission_acc = exio3_data.filt_AR5.loc[seller_ISO]
    emission_acc.reset_index(inplace=True, drop=True)
    emission_cpv = emission_acc.loc[emission_acc['product'] == exio_dict[curr_cont['cpv']]]
    GWP_cpv = emission_cpv['kg CO2 eq / M.Euro'].values
    total_emission = (curr_cont['precoContratual']/1e6) * GWP_cpv[0]
    entry = {
        'idcontrato': c_ID,
        'objectoContrato': curr_cont['objectoContrato'],
        'cpv': curr_cont['cpv'],
        'dataCelebracaoContrato': curr_cont['dataCelebracaoContrato'],
        'precoContratual': curr_cont['precoContratual'],
        'kg CO2 eq': total_emission,
        'percentage of total emissions (%)': 100*total_emission/exio3_fp.values[0]
    }
    public_report.loc[len(public_report)] = entry

