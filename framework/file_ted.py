import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import wordnet as wn
from unidecode import unidecode

class TEDfiles:
    def __init__(self):
        self.path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/"
        self.file = "TED_award_2018-2022.csv"
        self.lang = str()
        self.raw_dataframe = pd.DataFrame()
        self.query_dataframe = pd.DataFrame()
        self.filtered_query = pd.DataFrame()
        self.variants = []
        self.entries = list()
        self.gpp_teds = list()
        self.total_teds = list()
        self.gpp_oriented_teds = pd.DataFrame()
        self.gpp_tender_ratio = list()

    def read(self, country_code, lang):
        self.lang = lang
        self.raw_dataframe = pd.read_csv(self.path + self.file, sep=',')
        self.query_dataframe = self.raw_dataframe.query('ISO_COUNTRY_CODE == "%s"' % country_code)
        self.pre_proc()

        return self.query_dataframe

    def cpv_main_group_extractor(self, cpv):
        return cpv[:2]

    def pre_proc(self):
        num_columns = ["ID_NOTICE_CAN", "ID_TYPE", "DT_DISPATCH", "YEAR", "CAE_TYPE", "CPV", "VALUE_EURO",
                       "LOTS_NUMBER",
                       "B_GPA", "CRIT_CODE", "AWARD_VALUE_EURO", "NUMBER_AWARDS"]
        txt_columns = ["CAE_NAME", "MAIN_ACTIVITY", "CRIT_CRITERIA",
                       "WIN_COUNTRY_CODE", "TITLE", "TYPE_OF_CONTRACT", "INFO_ON_NON_AWARD"]
        self.filtered_query = self.query_dataframe[num_columns + txt_columns]

        for txt in txt_columns:
            self.filtered_query[txt] = self.filtered_query[txt].str.lower()
            self.filtered_query[txt] = self.filtered_query[txt].str.normalize('NFKD').str.\
                encode('ascii', errors='ignore').str.decode('utf-8')

        self.filtered_query["DT_DISPATCH"] = pd.to_datetime(self.filtered_query["DT_DISPATCH"]).dt.date
        self.filtered_query.drop(self.filtered_query[self.filtered_query["CRIT_CODE"] == 'L'].index, inplace=True)
        self.filtered_query.dropna(subset=["CRIT_CODE"], inplace=True)
        self.filtered_query.drop(self.filtered_query[self.filtered_query["INFO_ON_NON_AWARD"].\
                                 notna() == True].index, inplace=True)
        self.filtered_query["CPV"] = self.filtered_query["CPV"].astype(str)
        self.filtered_query["main_CPV"] = self.filtered_query["CPV"].apply(self.cpv_main_group_extractor)
        self.filtered_query = self.filtered_query.drop_duplicates(subset='ID_NOTICE_CAN', keep='first')

    def gpp_vocab(self):
        #nltk.download("wordnet")
        #nltk.download('omw-1.4')

        words_to_filter = ["ambiental", "sustentável", "emissão", "poluente", "energia", "renovável"]
        for words in words_to_filter:
            related = wn.synsets(words, lang=self.lang)
            for related in related:
                for lemma in related.lemmas(lang=self.lang):
                    self.variants.extend(lemma.synset().lemma_names(lang=self.lang))
        self.variants = list(set(self.variants))

        remove = ["programa", "fornecimento", "envio"]
        filt_variants = [word for word in self.variants if word not in remove]
        self.variants = filt_variants.copy()
        for i in range(len(self.variants)):
            self.variants[i] = unidecode(self.variants[i])

    def gpp_oriented_filt(self):
        self.gpp_vocab()
        grouped_frame = self.filtered_query.groupby(self.filtered_query['YEAR'])
        self.entries = list(grouped_frame.groups.keys())
        for grp in self.entries:
            curr_group = grouped_frame.get_group(grp)
            self.total_teds.append(len(curr_group))
            bool_gpp = curr_group['CRIT_CRITERIA'].str.contains('|'.join(self.variants), case=False)
            idx_gpp = np.where(bool_gpp == True)
            self.gpp_oriented_teds = pd.concat([self.gpp_oriented_teds, curr_group.iloc[idx_gpp[0]]])
            self.gpp_teds.append(len(curr_group.iloc[idx_gpp[0]]))

        return self.gpp_oriented_teds

    def GTR(self, plot=False):
        for year in range(len(self.entries)):
            self.gpp_tender_ratio.append(self.gpp_teds[year] / self.total_teds[year])

        if plot:
            plt.figure(1)
            leg = list()
            plt.bar(self.entries, self.total_teds, width=0.4)
            leg.append("Total TEDs of the year")
            plt.bar(self.entries, self.gpp_teds, width=0.2, color='maroon')
            leg.append("GPP oriented TEDs of the year")
            plt.xlabel("Number of contracts")
            plt.ylabel("Year")
            plt.title("GPP oriented TEDs throughout the years 2018-2022")
            plt.show()

            plt.figure(2)
            plt.bar(self.entries, self.gpp_tender_ratio, width=0.4)
            plt.xlabel("GPP oriented tenders [%]")
            plt.ylabel("Year")
            plt.title("Percentage of GPP oriented TEDs throughout the years 2018-2022")
            plt.show()
