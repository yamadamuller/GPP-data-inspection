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
        self.Z = pd.DataFrame()
        self.Y = pd.DataFrame()
        self.x = pd.DataFrame()
        self.M = pd.DataFrame()

    def read(self):
        print(f'[Class {self.__class__.__name__}] Reading {self.file}...')

        files = list()
        names = ['Z', 'Y', 'M']
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
            self.M = pklIO.pop()

        else:
            self.exio_raw = pymrio.parse_exiobase3(path=self.path + self.file)

            self.Z = self.exio_raw.Z
            self.Y = self.exio_raw.Y
            self.M = self.exio_raw.satellite.M

            to_pkl = [self.Z, self.Y, self.M]
            for par in range(len(to_pkl)):
                to_pkl[par].to_pickle(self.path + 'pkls/' + f'{names[par] + str(self.year)}.pkl')

        self.regFilter()
        print(f'[Class {self.__class__.__name__}] {self.file} read!')

        return self.M, self.Y, self.Z

    def regFilter(self):
        if self.region_filter:
            line_idx = list()
            for ln in range(len(self.Z.index)):
                if (self.Z.index[ln])[0] in self.ISO_code:
                    line_idx.append(ln)

            clm_idx = list()
            for clm in range(len(self.Y.columns)):
                if (self.Y.columns[clm])[0] in self.ISO_code:
                    clm_idx.append(clm)

            self.Z = self.Z.iloc[line_idx, line_idx]
            self.Y = self.Y.iloc[line_idx, clm_idx]
            self.M = self.M.iloc[:,line_idx]

    def StructAlgebra(self):
        final_demand = (self.Y @ np.ones((np.shape(self.Y)[1], 1)))
        my_x = np.linalg.inv(np.eye(len(self.A)) - self.A) @ final_demand
        #ouput in M.EUR for the given demand Y
        print(f'[Output matrix x] MSE = {mean_squared_error(self.x.values, my_x.values)}')

        my_M = self.exio_raw.satellite.S @ np.linalg.inv(np.eye(len(self.A)) - self.A)
        #direct and indirect requirements for the respective unit of column output
        print(f'[Requirements matrix M] MSE = '
              f'{mean_squared_error(self.exio_raw.satellite.M.values, my_M.values)}')

        my_D_cba = self.exio_raw.satellite.M.copy()
        my_D_cba = my_M * final_demand.values.T
        #total values in the respective unit for the given characterization factor
        print(f'[Consumption based accounting] MSE = '
              f'{mean_squared_error(self.exio_raw.satellite.D_cba.values, my_D_cba.values)}')