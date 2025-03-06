import numpy as np
import pandas as pd
import os

class EXIOfiles:
    def __init__(self, ISO_country_code, IOT_year, analysis='product', type_cons='all'):
        self.absolute_path = os.path.abspath('..')
        self.analysis = analysis
        self.IOT_year = IOT_year
        if self.analysis == 'product':
            self.data_path = os.path.join(self.absolute_path, f"data/exiobase/IOT_{self.IOT_year}_pxp/")
        elif self.analysis == 'industry':
            self.data_path = os.path.join(self.absolute_path, f"data/exiobase/IOT_{self.IOT_year}_ixi/")
        else:
            raise ValueError(f"[Class {self.__class__.__name__}] Exiobase accepts only pxp or ixi formats!")

        self.type_cons = type_cons

        if isinstance(ISO_country_code, list):
            self.ISO_code = ISO_country_code
        else:
            self.ISO_code = [ISO_country_code]

        self.Y = pd.DataFrame()
        self.S = pd.DataFrame()
        self.M = pd.DataFrame()
        self.AR5 = pd.DataFrame()
        self.F_Y = pd.DataFrame()
        self.S_Y = pd.DataFrame()
        self.filt_Y = pd.DataFrame()
        self.filt_S = pd.DataFrame()
        self.filt_AR5 = pd.DataFrame()
        self.filt_FY = pd.DataFrame()
        self.filt_SY = pd.DataFrame()
        self.filt_M = pd.DataFrame()
        self.f_cons_emission = pd.DataFrame()
        self.sum_filt_Y = pd.DataFrame()
        self.final_cons_acc = pd.DataFrame()
        self.final_dir_cons_acc = pd.DataFrame()
        self.footprint = pd.DataFrame()
        self.dir_footprint = pd.DataFrame()
        self.direct_emission_acc = pd.DataFrame()
        self.EU_pop = [8300788, 10625700, 7659764, 1063095, 10334160, 82266372, 5461438, 1341672, 44878945, 5288720,
                       64012572, 11192763, 10055780, 4356931, 59375289, 3375618, 479993, 2276100, 409050,
                       16381696, 38120560, 10608335, 21546873, 9148092, 2018122, 5397318, 60986649]

    def ISO_code_extractor(self, flow):
        return flow[:2]

    def GWP_element_extractor(self, flow):
        return flow[:3]

    def rearranger(self, filt_df, index=False):
        if 'GB' in self.ISO_code:
            if index:
                updated = [idx for idx in filt_df.index if idx != 'GB'] + ['GB']
            else:
                updated = [col for col in filt_df.columns if col != 'GB'] + ['GB']
        else:
            updated = self.ISO_code

        if index:
            output = filt_df.reindex(index=updated)
        else:
            output = filt_df.reindex(columns=updated)
        return output

    def read(self):
        print(f'[Class {self.__class__.__name__}] Reading Exiobase 3 {self.analysis} data...')
        #reading the exiobase 3 .txt files of interest
        self.Y = pd.read_csv(self.data_path + '/Y.txt', sep='\t', low_memory=False)
        self.S = pd.read_csv(self.data_path + 'impacts/S.txt', sep='\t', low_memory=False)
        self.M = pd.read_csv(self.data_path + 'satellite/M.txt', sep='\t', low_memory=False)
        self.AR5 = pd.read_csv(self.data_path + 'impacts/M.txt', sep='\t', low_memory=False)
        self.F_Y = pd.read_csv(self.data_path + 'impacts/F_Y.txt', sep='\t', low_memory=False)
        self.S_Y = pd.read_csv(self.data_path + 'impacts/S_Y.txt', sep='\t', low_memory=False)

        #Formating the dataframes with similar formats
        df_dict = {'M': self.M, 'Y': self.Y}
        for curr_df in df_dict.keys():
            df_dict[curr_df].loc[len(df_dict[curr_df])] = df_dict[curr_df].columns
            df_dict[curr_df].iloc[-1, 1:] = df_dict[curr_df].iloc[-1, 1:].apply(self.ISO_code_extractor)
            df_dict[curr_df].columns = df_dict[curr_df].values[0]
            df_dict[curr_df] = df_dict[curr_df].iloc[2:, :]
        self.M = df_dict['M']
        self.Y = df_dict['Y']
        self.Y.reset_index(inplace=True, drop=True)

        em_dict = {'AR5': self.AR5, 'F_Y': self.F_Y, 'S': self.S, 'S_Y': self.S_Y}
        for curr_em in em_dict.keys():
            em_dict[curr_em] = em_dict[curr_em][em_dict[curr_em].region.isin(
                ['sector', 'GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)'])].transpose().reset_index()
            em_dict[curr_em].columns = em_dict[curr_em].values[0]
            em_dict[curr_em] = em_dict[curr_em].iloc[1:]
            em_dict[curr_em]['region'] = em_dict[curr_em]['region'].apply(self.ISO_code_extractor)
        self.AR5 = em_dict['AR5']
        self.AR5.columns = ['region', 'product', 'kg CO2 eq / M.Euro']
        self.F_Y = em_dict['F_Y']
        self.F_Y.columns = ['region', 'kg CO2 eq / final consumption']
        self.S = em_dict['S']
        self.S.columns = ['region', 'product', 'kg CO2 eq / M.Euro']
        self.S_Y = em_dict['S_Y']
        self.S_Y.columns = ['region', 'kg CO2 eq / final consumption']

        #run filters and prepare the data
        self.reg_filter()
        self.cons_filter()
        self.gwp_filter()
        self.data_prep()
        print(f'[Class {self.__class__.__name__}] Exiobase 3 data read!')

    def reg_filter(self):
        if len(self.ISO_code) < 44:
            self.Y.rename(columns={np.nan: 'product'}, inplace=True)

            ISO_cons_idx = list()
            for cons in range(len(self.Y.iloc[-1,:])):
                if self.Y.iloc[-1,cons] in self.ISO_code:
                    ISO_cons_idx.append(cons)
            self.filt_Y = self.Y.iloc[:, ISO_cons_idx]

            ISO_final_idx = list()
            for final_ISO in range(len(self.F_Y['region'])):
                if self.F_Y['region'].values[final_ISO] in self.ISO_code:
                    ISO_final_idx.append(final_ISO)

            self.filt_FY = self.F_Y.iloc[ISO_final_idx, :]
            self.filt_FY['kg CO2 eq / final consumption'] = self.filt_FY['kg CO2 eq / final consumption'].astype(float)
            self.filt_SY = self.S_Y.iloc[ISO_final_idx, :]
            self.filt_SY['kg CO2 eq / final consumption'] = self.filt_SY['kg CO2 eq / final consumption'].astype(float)
        else:
            self.filt_Y = self.Y
            self.filt_FY = self.F_Y
            self.filt_SY = self.S_Y

        self.filt_AR5 = self.AR5
        self.filt_AR5.reset_index(inplace=True, drop=True)
        #final_demand = self.Y.iloc[:-1, 2:].astype(float).sum(axis=1)
        #final_demand = 1/final_demand
        #idx_desc = np.where(final_demand == np.inf)
        #final_demand[idx_desc[0]] = 0
        #self.S['kg CO2 eq / M.Euro'] = self.S['kg CO2 eq / M.Euro'].astype(float).multiply(final_demand.values, axis='index')
        self.filt_S = self.S
        self.filt_S.reset_index(inplace=True, drop=True)
        self.filt_Y.reset_index(inplace=True, drop=True)
        self.filt_FY.reset_index(inplace=True, drop=True)
        self.filt_SY.reset_index(inplace=True, drop=True)

    def cons_filter(self):
        if self.type_cons == 'government':
            cols_to_filter = ['Final consumption expenditure by government',
                              'Gross fixed capital formation']
        elif self.type_cons == 'household':
            cols_to_filter = ['Final consumption expenditure by households',
                              'Gross fixed capital formation']
        elif self.type_cons == 'non-profit':
            cols_to_filter = ['Final consumption expenditure by non-profit organisations serving households (NPISH)',
                              'Gross fixed capital formation']
        elif self.type_cons == 'all':
            cols_to_filter = ['Final consumption expenditure by households',
                              'Final consumption expenditure by non-profit organisations serving households (NPISH)',
                              'Final consumption expenditure by government',
                              'Gross fixed capital formation']
        else:
            raise ValueError(f"[Class {self.__class__.__name__}] Type of consumption accounting not specified!")

        self.filt_Y = self.filt_Y[cols_to_filter]
        self.filt_Y.columns = self.filt_Y.iloc[-1,:]
        self.filt_Y = self.filt_Y.iloc[:-1,:]
        self.filt_Y = self.filt_Y.T
        self.sum_filt_Y = self.filt_Y.astype(float).groupby(self.filt_Y.index)
        self.sum_filt_Y = self.sum_filt_Y.sum()
        self.sum_filt_Y = self.sum_filt_Y.T
        self.filt_Y = self.filt_Y.T

        #rearrange the columns
        self.sum_filt_Y = self.rearranger(self.sum_filt_Y)
        self.sum_filt_Y.index = self.Y['category'].values[:-1]
        self.sum_filt_Y['product'] = self.Y['product'].values[:-1]

    def gwp_filter(self):
        GWP_idx = list()
        stressor_GWP = ['CO2', 'N2O', 'CH4', 'PFC', 'HFC', 'SF6', 'CF4', 'NF3'] #TODO: GHG acc based on beylot2019
        GWP_convert = {'CO2': 1, 'N2O': 265, 'CH4': 28, 'PFC': 1, 'HFC': 1,
                       'SF6': 23500, 'CF4': 6630, 'NF3': 16600}
        #stressor_GWP = ['CO2', 'N2O', 'CH4']
        #GWP_convert = {'CO2': 1, 'N2O': 265, 'CH4': 28}
        stressor_cat = self.M['sector'].tolist()
        stressor_split = [strg.split() for strg in stressor_cat]
        for i in range(len(stressor_split)):
            for j in stressor_GWP:
                if j in stressor_split[i]:
                    GWP_idx.append(i)
                    break
                else:
                    continue

        self.filt_M = self.M.iloc[GWP_idx,:]
        self.filt_M.loc[len(self.filt_M)] = self.M.iloc[-1,:]
        self.filt_M.reset_index(inplace=True, drop=True)
        self.filt_M['sector'] = self.filt_M['sector'].apply(self.GWP_element_extractor)

        conv_mat = np.zeros((len(self.filt_M.index)-1,1))
        for stressor in range(np.shape(conv_mat)[0]):
            conv_mat[stressor] = GWP_convert[self.filt_M['sector'].iloc[:-1].values[stressor]]

        fp_dic = {'filtM': self.filt_M}
        for curr_fp in fp_dic.keys():
            fp_dic[curr_fp] = fp_dic[curr_fp].iloc[:-1,1:].astype(float) * conv_mat
            fp_dic[curr_fp] = fp_dic[curr_fp].sum(axis=0)
            fp_dic[curr_fp] = pd.DataFrame(fp_dic[curr_fp])
        self.filt_M = fp_dic['filtM']
        self.filt_M.rename(columns={0: 'kg CO2 eq / M.Euro'}, inplace=True)

    def data_prep(self):
        self.sum_filt_Y.iloc[:,:-1] = self.sum_filt_Y.iloc[:,:-1].astype(float)
        self.filt_AR5['kg CO2 eq / M.Euro'] = self.filt_AR5['kg CO2 eq / M.Euro'].astype(float)
        self.filt_S['kg CO2 eq / M.Euro'] = self.filt_S['kg CO2 eq / M.Euro'].astype(float)
        self.filt_FY['kg CO2 eq / final consumption'] = self.filt_FY['kg CO2 eq / final consumption'].astype(float)
        self.filt_SY['kg CO2 eq / final consumption'] = self.filt_SY['kg CO2 eq / final consumption'].astype(float)
        self.filt_M['kg CO2 eq / M.Euro'] = self.filt_M['kg CO2 eq / M.Euro'].astype(float)
        grouped_FY = self.filt_FY.groupby('region')
        grouped_SY = self.filt_SY.groupby('region')
        self.final_cons_acc = grouped_FY.head(3).groupby('region').sum().reset_index()
        self.final_cons_acc['ton CO2 eq / final consumption'] = self.final_cons_acc['kg CO2 eq / final consumption']/1000
        self.final_cons_acc.index = self.final_cons_acc['region']
        self.final_cons_acc = self.rearranger(self.final_cons_acc, index=True)
        self.final_dir_cons_acc = grouped_SY.head(3).groupby('region').sum().reset_index()
        self.final_dir_cons_acc['ton CO2 eq / final consumption'] = self.final_dir_cons_acc['kg CO2 eq / final consumption']/1000
        self.final_dir_cons_acc.index = self.final_dir_cons_acc['region']
        self.final_dir_cons_acc = self.rearranger(self.final_dir_cons_acc, index=True)

    def emission_estimator(self, AR5=True, per_capita=False):
        self.footprint = self.sum_filt_Y.iloc[:,:-1]

        if AR5:
            self.footprint = self.footprint.multiply(self.filt_AR5['kg CO2 eq / M.Euro'].values, axis='index')
        else:
            self.footprint = self.footprint.multiply(self.filt_M['kg CO2 eq / M.Euro'].values, axis='index')

        self.footprint['product'] = self.sum_filt_Y['product']
        updated_cols = ['product'] + [col for col in self.footprint.columns if col != 'product']
        self.footprint = self.footprint.reindex(columns=updated_cols)
        sum_footprint = (self.footprint.iloc[:,1:].sum(axis=0))/1000
        #sum_footprint = (self.footprint.iloc[:, 1:].sum(axis=0))
        final_cons = self.final_cons_acc['ton CO2 eq / final consumption']
        GHG_footprint = sum_footprint.add(final_cons.values)
        #GHG_footprint = sum_footprint
        if per_capita:
            if len(self.EU_pop) != 27:
                raise ValueError(f"[Class {self.__class__.__name__}] Per capita information only available for EU27!")
            else:
                GHG_footprint = GHG_footprint/self.EU_pop
                return GHG_footprint
        else:
            return GHG_footprint

    def direct_emission_estimator(self):
        pkl_path = os.path.join(self.absolute_path,
                   f"data/exiobase/direct_emissions/Iup_{self.IOT_year}_{self.analysis}.pkl")
        if os.path.isfile(pkl_path):
            self.direct_emission_acc = pd.read_pickle(pkl_path)
            return self.direct_emission_acc
        else:
            self.direct_emission_acc = self.generate_factors(pkl_path)
            return self.direct_emission_acc

    def generate_factors(self, path_to_pkl):
        print(f'[Class {self.__class__.__name__}] Generating direct emission requirement factors data...')
        A = pd.read_csv(self.data_path + '/A.txt', sep='\t', low_memory=False)
        df_dict = {'A': A}
        for curr_df in df_dict.keys():
            df_dict[curr_df].loc[len(df_dict[curr_df])] = df_dict[curr_df].columns
            df_dict[curr_df].iloc[-1, 1:] = df_dict[curr_df].iloc[-1, 1:].apply(self.ISO_code_extractor)
            df_dict[curr_df].columns = df_dict[curr_df].values[0]
            df_dict[curr_df] = df_dict[curr_df].iloc[2:, :]
        A = df_dict['A']
        A.index = A[np.nan]

        # Accounting the direct impact
        output = pd.DataFrame(self.filt_S['kg CO2 eq / M.Euro']).T @ A.iloc[:-1, 2:].astype(float).values
        output = output.T
        output.index = self.filt_S.index
        output['product'] = self.filt_S['product'].values
        updated_cols = ['product', 'kg CO2 eq / M.Euro']
        output = output.reindex(columns=updated_cols)
        output.to_pickle(path_to_pkl)
        print(f'[Class {self.__class__.__name__}] Direct emission requirement factors data generated!')
        return output

    def direct_emissions_valid(self):
        pkl_path = os.path.join(self.absolute_path, f"data/exiobase/direct_emissions/Iup_{self.IOT_year}_{self.analysis}.pkl")
        if os.path.isfile(pkl_path):
            I_up = pd.read_pickle(pkl_path)
            self.dir_footprint = self.sum_filt_Y.iloc[:,:-1].multiply(I_up['kg CO2 eq / M.Euro'].values, axis='index')
            self.dir_footprint['product'] = self.sum_filt_Y['product']
            update_cols = ['product'] + [col for col in self.dir_footprint.columns if col != 'product']
            self.dir_footprint = self.dir_footprint.reindex(columns=update_cols)
            sum_direct = self.dir_footprint.iloc[:,1:].sum(axis=0)
            final_cons = self.final_dir_cons_acc['kg CO2 eq / final consumption']
            GHG_dir_footprint = sum_direct.add(final_cons)
            return GHG_dir_footprint
        else:
            self.generate_factors(pkl_path)
            return self.direct_emissions_valid()
