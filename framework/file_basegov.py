import numpy as np
import pandas as pd

class BASEGOVfiles:
    def __init__(self, years='hist'):
        if years == 'hist':
            self.years = np.arange(2012, 2023, 1)
        else:
            self.years = years

        self.path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/"
        self.raw_dataframe = pd.DataFrame()
        self.fill_dataframe = pd.DataFrame()
        self.NIPC = list()
        self.OldFormat = list()

    def read(self):
        for yr in self.years:
            curr_df = pd.read_csv(self.path + f'contratos{yr}.csv', sep=',')

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
