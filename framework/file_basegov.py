import numpy as np
import pandas as pd
import os

class BASEGOVfiles:
    def __init__(self, years='hist'):
        if years == 'hist':
            self.years = np.arange(2012, 2023, 1)
        else:
            if isinstance(years, list):
                self.years = years
            else:
                self.years = [years]

        self.absolute_path = os.path.abspath('..')
        self.raw_dataframe = pd.DataFrame()
        self.fill_dataframe = pd.DataFrame()
        self.NIPC = list()
        self.OldFormat = list()

    def read(self):
        for yr in self.years:
            print(f'[Class {self.__class__.__name__}] Reading basegov {yr} data...')
            curr_data_path = os.path.join(self.absolute_path, f"data/basegov/contratos{yr}.csv")
            curr_df = pd.read_csv(curr_data_path, sep=',')

            if curr_df.columns[2] == 'tipoContrato':
                self.OldFormat.append(True)
                if curr_df.columns[10] != 'cpv':
                    self.NIPC.append(True)
                else:
                    self.NIPC.append(False)
                curr_df.rename(columns={'adjudicante': 'entidade_compradora'}, inplace=True)
            else:
                self.OldFormat.append(False)
                self.NIPC.append(True)
                curr_df.rename(columns={'entidade_comunicante': 'entidade_compradora'}, inplace=True)

            self.raw_dataframe = pd.concat([self.raw_dataframe, curr_df], ignore_index=True)

        print(f'[Class {self.__class__.__name__}] Basegov file(s) read!')
        self.pre_proc()

        return self.fill_dataframe

    def pre_proc(self):
        self.fill_dataframe = self.raw_dataframe.copy()
        for clm in self.raw_dataframe.columns:
            if pd.isnull(self.fill_dataframe[clm]).all():
                self.fill_dataframe.drop(clm, axis=1, inplace=True)

        self.fill_dataframe['entidade_compradora'] = self.fill_dataframe['entidade_compradora'].str.slice(start=11)

        nAn_celeb = len(self.fill_dataframe.loc[self.fill_dataframe['dataCelebracaoContrato'] == ''])
        nAn_publi = len(self.fill_dataframe.loc[self.fill_dataframe['dataPublicacao'] == ''])
        if nAn_celeb > nAn_publi:
            self.fill_dataframe.drop(['dataCelebracaoContrato'], axis=1, inplace=True)
        else:
            self.fill_dataframe.drop(['dataPublicacao'], axis=1, inplace=True)

        #Normalizing contracted object entries
        self.fill_dataframe['objectoContrato'] = self.fill_dataframe['objectoContrato'].str.lower()
        self.fill_dataframe['objectoContrato'] = self.fill_dataframe['objectoContrato'].str.normalize('NFKD'). \
            str.encode('ascii', errors='ignore').str.decode('utf-8')

        #filtering only the cpv numbers
        self.fill_dataframe['cpv'] = self.fill_dataframe['cpv'].str.normalize('NFKD').\
                                     str.encode('ascii', errors='ignore').str.decode('utf-8')
        self.fill_dataframe['cpv'] = self.fill_dataframe['cpv'].str.slice(0,8)

        #Making the ID of the contract the index
        self.fill_dataframe.index = self.fill_dataframe['idcontrato']
