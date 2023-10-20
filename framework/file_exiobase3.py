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

        self.regFilter()
        #self.footprint_est()
        print(f'[Class {self.__class__.__name__}] {self.file} read!')

        return self.A, self.Dcba, self.F, self.M, self.Y, self.x

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
            for strs in range(len(self.F.columns)):
                if (self.F.columns[strs])[0] in self.ISO_code:
                    strs_idx.append(strs)

            self.A = self.A.iloc[line_idx, line_idx]
            self.Y = self.Y.iloc[line_idx, clm_idx]
            self.safe_Y = self.Y
            self.M = self.M.iloc[:,line_idx]
            self.F = self.F.iloc[:,strs_idx]
            self.Dcba = self.Dcba.iloc[:,line_idx]
            self.x = self.x.iloc[line_idx, clm_idx]

    def leontief(self):
        if self.household:
            house_occ = np.arange(0,len(self.Y.columns.values),7)
            self.Y = self.Y.iloc[:, house_occ]

        self.f = self.Y @ np.ones((np.shape(self.Y)[1],1))
        self.L = np.linalg.inv(np.eye(len(self.A)) - self.A)
        self.output = self.L @ self.f
        self.output.rename(columns={0: "output"}, inplace=True)
        self.output.index = self.f.index
        reg = list()
        for idx in range(len(self.f.index)):
            reg.append(self.f.index[idx][0])
        self.output['ISO_code'] = reg

    def GWP_element_extractor(self,flow):
        return flow[:3]

    def stressFilt(self):
        GWP_idx = list()
        stressor_GWP = ['CO2', 'N2O', 'CH4', 'SF6']
        stressor_idx = self.F.index.tolist()
        for i in range(len(stressor_idx)):
            for j in stressor_GWP:
                if stressor_idx[i].find(j) != -1:
                    GWP_idx.append(i)
                    continue

        self.total_stressor = self.F.iloc[GWP_idx,:]
        self.total_stressor.reset_index(inplace=True)
        self.total_stressor['stressor'] = self.total_stressor['stressor'].apply(self.GWP_element_extractor)

        #Characterization factor (kg -> kg CO2 eq)
        GW_convert = {'CO2': 1, 'N2O': 298, 'CH4': 25, 'SF6': 22800}
        conv_mat = np.zeros((len(self.total_stressor['stressor']), 1))
        for stressor in range(np.shape(conv_mat)[0]):
            conv_mat[stressor] = GW_convert[self.total_stressor['stressor'].values[stressor]]
        self.total_stressor.drop('stressor', axis=1, inplace=True)
        self.total_stressor = self.total_stressor * conv_mat

        #household accounting test
        f_hh = self.safe_Y @ np.ones((np.shape(self.safe_Y)[1], 1))
        total_req = self.M @ np.diagflat(f_hh)
        invMat = self.Dcba - total_req.values
        conv_invMat = invMat.iloc[GWP_idx, :]
        conv_invMat = conv_invMat * conv_mat
        conv_invMat = conv_invMat.iloc[:self.idx_stress, :]
        self.sum_invMat = conv_invMat.sum(axis=0)

    def inventory(self):
        #environmental matrix
        x_hat = np.diagflat(1/self.output['output'])
        x_hat[np.where(x_hat == np.inf)] = 0
        B = self.total_stressor.iloc[:self.idx_stress, :] @ x_hat

        #inventory vector per capita
        EU_pop = 493000000
        g = B @ self.L
        g = g.sum(axis=0)
        self.footprint = g @ np.diagflat(self.f) + self.sum_invMat
        self.footprint /= EU_pop
        self.footprint = pd.DataFrame(self.footprint)
        self.footprint.index = self.A.index

    def footprint_est(self):
        #run calculation functions
        self.leontief()
        self.stressFilt()
        self.inventory()
