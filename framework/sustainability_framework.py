import json
import os
import pandas as pd
import warnings
from framework import file_basegov, file_exiobase3

class sustainability:
    def __init__(self, year, ISO_code, proc_obj=None, ID=None):
        self.year = year
        self.ISO_code = ISO_code
        self.proc_obj = proc_obj

        if ID is None:
            self.ID = ID
        else:
            if isinstance(ID, list):
                self.ID = ID
            else:
                self.ID = [ID]

        self.absolute_path = os.path.abspath('..')
        self.total_ISO_emissions = pd.Series()
        self.basegov_data = pd.DataFrame()
        self.exio3_data = None
        self.exio_dict = {}
        self.nace_dict = {}
        self.cpv_dict = {}
        self.contracts_ID = list()
        self.report = None

    def read_files(self):
        #Reading the basegov and exiobase 3 files
        basegov = file_basegov.BASEGOVfiles(years=self.year)
        self.basegov_data = basegov.read()
        self.exio3_data = file_exiobase3.EXIOfiles(self.ISO_code, self.year, analysis='industry', type_cons='government')
        self.exio3_data.read()
        self.total_ISO_emissions = 1000*self.exio3_data.emission_estimator()

        #importing the CPV to exiobase product dictionary
        dict_path = os.path.join(self.absolute_path, "data/conversions/CPV_NACE/cpv_exio_dict.json")
        with open(dict_path, 'r') as json_file:
            self.exio_dict = json.load(json_file)

        # Importing the CPV to NACE industry dictionary
        dict_path = os.path.join(self.absolute_path, "data/conversions/CPV_NACE/cpv_cpa_dict.json")
        with open(dict_path, 'r') as json_file:
            self.nace_dict = json.load(json_file)

        # Importing the NACE to EXIOBASE industry dictionary
        dict_path = os.path.join(self.absolute_path, "data/conversions/CPV_NACE/nace_exio_dict.json")
        with open(dict_path, 'r') as json_file:
            self.cpv_dict = json.load(json_file)

    def filt_contracts(self):
        #searching for the contracts involving public procurement of self.proc_obj
        occ_obj = self.basegov_data['objectoContrato'].str.contains(self.proc_obj).fillna(False)
        self.basegov_data = self.basegov_data[occ_obj]

        #populating the contracts_ID list based on the basegov filtering
        for ID in self.basegov_data.index:
            self.contracts_ID.append(ID)

    def report_emission(self, stats):
        #creating the dataframe containing the emission data for the contract
        self.exio3_data.filt_AR5.index = self.exio3_data.filt_AR5['region']
        self.exio3_data.filt_AR5.drop('region', axis=1, inplace=True)
        self.exio3_data.filt_S.index = self.exio3_data.filt_S['region']
        self.exio3_data.filt_S.drop('region', axis=1, inplace=True)
        cols = ['Contract ID', 'Contract object', 'CPV', 'NACE', 'Celebration date', 'Contract price (€)',
                'Total emissions (kg CO2 eq)', 'Direct emissions (kg CO2 eq)', 'Indirect emissions (kg CO2 eq)',
                'Percentage of NACE code total emissions (%)', 'Percentage of the industry total emissions (%)']
        self.report = pd.DataFrame(columns=cols)
        for ID in self.contracts_ID:
            #ID based info
            curr_cont = self.basegov_data.loc[ID]
            seller_ISO = 'PT' #TODO: revalidar com contrato estrangeiros
            nace_code = self.nace_dict[curr_cont['cpv']][0]

            #NACE based footprints
            total_idx = self.exio3_data.footprint['product'].isin(self.cpv_dict[nace_code])
            ind_idx = self.exio3_data.footprint['product'].isin([self.exio_dict[curr_cont['cpv']]])
            total_nace_fp = self.exio3_data.footprint[total_idx]
            ind_fp = self.exio3_data.footprint[ind_idx]
            total_nace_fp = total_nace_fp.sum(axis=0)
            ind_fp = ind_fp.sum(axis=0)

            #Emissions accounting given the CPV
            total_emission_acc = self.exio3_data.filt_AR5.loc[seller_ISO]
            total_emission_acc.reset_index(inplace=True, drop=True)
            total_emission_cpv = total_emission_acc.loc[total_emission_acc['product'] == self.exio_dict[curr_cont['cpv']]]
            direct_emission_acc = self.exio3_data.direct_emission_estimator().loc[seller_ISO]
            direct_emission_acc.reset_index(inplace=True, drop=True)
            direct_emission_cpv = direct_emission_acc.loc[direct_emission_acc['product'] == self.exio_dict[curr_cont['cpv']]]
            GWP_total = total_emission_cpv['kg CO2 eq / M.Euro'].values
            GWP_direct = direct_emission_cpv['kg CO2 eq / M.Euro'].values
            contract_total_emission = (curr_cont['precoContratual']/1e6) * GWP_total[0]
            contract_direct_emission = (curr_cont['precoContratual'] / 1e6) * GWP_direct[0]
            entry = {
                'Contract ID': ID,
                'Contract object': curr_cont['objectoContrato'],
                'CPV': curr_cont['cpv'],
                'NACE': nace_code,
                'Celebration date': curr_cont['dataCelebracaoContrato'],
                'Contract price (€)': curr_cont['precoContratual'],
                'Total emissions (kg CO2 eq)': contract_total_emission,
                'Direct emissions (kg CO2 eq)': contract_direct_emission,
                'Indirect emissions (kg CO2 eq)': contract_total_emission - contract_direct_emission,
                'Percentage of NACE code total emissions (%)': 100*contract_total_emission/total_nace_fp[self.ISO_code],
                'Percentage of the industry total emissions (%)': 100*contract_total_emission/ind_fp[self.ISO_code]
            }
            self.report.loc[len(self.report)] = entry
            #TODO: separar as direct emissions em scope 2 e 3
        if stats:
            print(f'Total {self.ISO_code} emissions (kg CO2 eq) = {self.total_ISO_emissions.values[0]}')
            total_acc = 100*self.report['Total emissions (kg CO2 eq)'].sum(axis=0)/self.total_ISO_emissions.values[0]
            print(f'All filtered contracts account for {total_acc}% of the total {self.ISO_code} emissions')
            print('Contract(s) emissions report:')
            with pd.option_context('display.max_rows', None,
                                   'display.max_columns', None,
                                   'display.precision', 5,
                                   ):
                print(self.report)
            print()

    def run(self, stats=False, debug=False):
        print(f'[Class {self.__class__.__name__}] Running FORCERA SUSTAINABILITY FRAMEWORK...')
        if not debug:
            warnings.simplefilter("ignore")

        self.read_files()
        #search for all IDs if the user didn't specify which
        if self.ID is None and self.proc_obj is not None:
            self.filt_contracts()
        else:
            self.contracts_ID = self.ID
        self.report_emission(stats)
        print(f'[Class {self.__class__.__name__}] FORCERA SUSTAINABILITY FRAMEWORK executed!')

        return self.report

