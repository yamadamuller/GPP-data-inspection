import numpy as np
import pandas as pd

class OPENTENDERfiles:
    def __init__(self, year = 'hist'):
        if year == 'hist':
            self.years = np.arange(2012, 2023, 1)
        else:
            self.years = year

        self.path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/"
        self.raw_dataframe = pd.DataFrame()
        self.fill_dataframe = pd.DataFrame()

    def read(self):
        for yr in self.years:
            curr_df = pd.read_csv(self.path + f'data-pt-{yr}.csv', sep=';', on_bad_lines='skip')
            self.raw_dataframe = pd.concat([self.raw_dataframe, curr_df], ignore_index=True)

        self.pre_proc()

        return self.fill_dataframe

    def pre_proc(self):
        self.fill_dataframe = self.raw_dataframe.copy()
        for clm in self.raw_dataframe.columns:
            if pd.isnull(self.raw_dataframe[clm]).all():
                self.fill_dataframe.drop(clm, axis=1, inplace=True)
