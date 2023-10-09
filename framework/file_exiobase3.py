import pymrio
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

class EXIOfiles:
    def __init__(self, ISO_country_code, region_filter=False):
        self.path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/exiobase/"
        self.file = "IOT_2017_ixi.zip"
        self.ISO_code = ISO_country_code
        self.region_filter = region_filter
        self.exio_raw = pd.DataFrame()
        self.Z = pd.DataFrame()
        self.Y = pd.DataFrame()
        self.A = pd.DataFrame()
        self.x = pd.DataFrame()
        self.L = pd.DataFrame()

    def read(self):
        self.exio_raw = pymrio.parse_exiobase3(path=self.path + self.file)

        if self.region_filter:
            line_idx = list()
            for idx in range(len(self.exio_raw.A.index)):
                if (self.exio_raw.A.index[idx])[0] == self.ISO_code:
                    line_idx.append(idx)

            clm_idx = list()
            for clm in range(len(self.exio_raw.Y.columns)):
                if (self.exio_raw.Y.columns[clm])[0] == self.ISO_code:
                    clm_idx.append(clm)

            self.Z = self.exio_raw.Z.iloc[line_idx, line_idx]
            self.Y = self.exio_raw.Y.iloc[line_idx, clm_idx]
            self.A = self.exio_raw.A.iloc[line_idx, line_idx]
            self.x = self.exio_raw.x.iloc[line_idx]
        else:
            self.Z = self.exio_raw.Z
            self.Y = self.exio_raw.Y
            self.A = self.exio_raw.A
            self.x = self.exio_raw.x

        self.L = np.linalg.inv(np.eye(len(self.A)) - self.A) #leontief matrix

        print(f'[Class {self.__class__.__name__}] {self.file} read!')

        return self.exio_raw

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