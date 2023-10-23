import pymrio
import numpy as np
import pandas as pd
import os
import pickle

class EXIOfiles:
    def __init__(self, ISO_country_code, IOT_year, region_filter=False, household=False):
        self.path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/exiobase/"
        self.file = f"IOT_{IOT_year}_pxp.zip"
        self.year = IOT_year

        if isinstance(ISO_country_code, list):
            self.ISO_code = ISO_country_code
        else:
            self.ISO_code = [ISO_country_code]

        self.region_filter = region_filter
        self.household = household
        self.exio_raw = pd.DataFrame()
        self.A = pd.DataFrame()
        self.Y = pd.DataFrame()
        self.x = pd.DataFrame()
        self.M = pd.DataFrame()
        self.F = pd.DataFrame()
        self.Dcba = pd.DataFrame()
        self.f = pd.DataFrame()
        self.L = np.array([])
        self.output = pd.DataFrame()
        self.total_stressor = pd.DataFrame()
        self.idx_stress = 13
        self.sum_invMat = pd.Series()
        self.footprint = pd.DataFrame()

    def read(self):
        print(f'[Class {self.__class__.__name__}] Reading {self.file}...')

        files = list()
        names = ['A', 'Dcba','F', 'M', 'Y','x']
        for nm in range(len(names)):
            files.append(names[nm] + str(self.year) + '.pkl')
        files.sort()

        if os.path.exists(self.path + 'pkls/' + files[0]):
            pklIO = list()
            for file in files:
                with open(self.path + 'pkls/' + file, 'rb') as curr_pkl:
                    pklIO.append(pickle.load(curr_pkl))

            self.x = pklIO.pop()
            self.Y = pklIO.pop()
            self.M = pklIO.pop()
            self.F = pklIO.pop()
            self.Dcba = pklIO.pop()
            self.A = pklIO.pop()

        else:
            self.exio_raw = pymrio.parse_exiobase3(path=self.path + self.file)

            self.A = self.exio_raw.A
            self.Y = self.exio_raw.Y
            self.M = self.exio_raw.impacts.M
            self.F = self.exio_raw.satellite.F
            self.Dcba = self.exio_raw.satellite.D_cba
            self.x = self.exio_raw.x

            to_pkl = [self.A, self.Dcba, self.F, self.M, self.Y, self.x]
            for par in range(len(to_pkl)):
                to_pkl[par].to_pickle(self.path + 'pkls/' + f'{names[par] + str(self.year)}.pkl')

        #self.regFilter()
        #self.footprint_est()
        print(f'[Class {self.__class__.__name__}] {self.file} read!')

        return self.A, self.Dcba, self.F, self.M, self.Y, self.x


