import pymrio
import numpy as np
import pandas as pd
import os
import pickle
from sklearn.metrics import mean_squared_error

class EXIOfiles:
    def __init__(self, ISO_country_code, IOT_year, region_filter=False):
        self.path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/exiobase/"
        self.file = f"IOT_{IOT_year}_pxp.zip"
        self.year = IOT_year

        if isinstance(ISO_country_code, list):
            self.ISO_code = ISO_country_code
        else:
            self.ISO_code = [ISO_country_code]

        self.region_filter = region_filter
        self.exio_raw = pd.DataFrame()
        self.A = pd.DataFrame()
        self.Y = pd.DataFrame()
        self.M = pd.DataFrame()
        self.S = pd.DataFrame()
        self.F = pd.DataFrame()
        self.Dcba = pd.DataFrame()
        self.Z = pd.DataFrame()

    def read(self):
        print(f'[Class {self.__class__.__name__}] Reading {self.file}...')

        files = list()
        names = ['A', 'Dcba','F', 'M', 'S', 'Y', 'Z']
        for nm in range(len(names)):
            files.append(names[nm] + str(self.year) + '.pkl')
        files.sort()

        if os.path.exists(self.path + 'pkls/' + files[0]):
            pklIO = list()
            for file in files:
                with open(self.path + 'pkls/' + file, 'rb') as curr_pkl:
                    pklIO.append(pickle.load(curr_pkl))

            self.Z = pklIO.pop()
            self.Y = pklIO.pop()
            self.S = pklIO.pop()
            self.M = pklIO.pop()
            self.F = pklIO.pop()
            self.Dcba = pklIO.pop()
            self.A = pklIO.pop()

        else:
            self.exio_raw = pymrio.parse_exiobase3(path=self.path + self.file)

            self.A = self.exio_raw.A
            self.Z = self.exio_raw.Z
            self.Y = self.exio_raw.Y
            self.M = self.exio_raw.satellite.M
            self.S = self.exio_raw.satellite.S
            self.F = self.exio_raw.satellite.F
            self.Dcba = self.exio_raw.satellite.D_cba

            to_pkl = [self.A, self.Dcba, self.F, self.M, self.S, self.Y, self.Z]
            for par in range(len(to_pkl)):
                to_pkl[par].to_pickle(self.path + 'pkls/' + f'{names[par] + str(self.year)}.pkl')

        self.regFilter()
        print(f'[Class {self.__class__.__name__}] {self.file} read!')

        return self.A, self.Dcba, self.F, self.M, self.S, self.Y, self.Z

    def regFilter(self):
        if self.region_filter:
            line_idx = list()
            for ln in range(len(self.A.index)):
                if (self.A.index[ln])[0] in self.ISO_code:
                    line_idx.append(ln)

            clm_idx = list()
            for clm in range(len(self.Y.columns)):
                if (self.Y.columns[clm])[0] in self.ISO_code:
                    clm_idx.append(clm)

            strs_idx = list()
            for strs in range(len(self.S.columns)):
                if (self.S.columns[strs])[0] in self.ISO_code:
                    strs_idx.append(strs)

            self.A = self.A.iloc[line_idx, line_idx]
            self.Z = self.Z.iloc[line_idx, line_idx]
            self.Y = self.Y.iloc[line_idx, clm_idx]
            self.M = self.M.iloc[:,line_idx]
            self.S = self.S.iloc[:,strs_idx]
            self.F = self.F.iloc[:,strs_idx]
            self.Dcba = self.Dcba.iloc[:,line_idx]
