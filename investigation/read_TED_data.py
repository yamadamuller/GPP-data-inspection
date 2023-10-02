import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import wordnet as wn
from unidecode import unidecode

#nltk.download("wordnet")
#nltk.download('omw-1.4')

def cpv_main_group_extractor(cpv):
    return cpv[:2]

path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/"
file = "TED_award_2018-2022.csv"

df = pd.read_csv(path+file, sep=',')
df2 = df.query("ISO_COUNTRY_CODE == 'PT'")

#DATA PREPROCESSING
num_columns = ["ID_NOTICE_CAN","ID_TYPE", "DT_DISPATCH", "YEAR", "CAE_TYPE", "CPV", "VALUE_EURO", "LOTS_NUMBER",
               "B_GPA", "CRIT_CODE","AWARD_VALUE_EURO", "NUMBER_AWARDS"]

txt_columns = ["CAE_NAME", "MAIN_ACTIVITY", "CRIT_CRITERIA",
               "WIN_COUNTRY_CODE", "TITLE", "TYPE_OF_CONTRACT", "INFO_ON_NON_AWARD"]
filt_df2 = df2[num_columns + txt_columns]

for txt in txt_columns:
    filt_df2[txt] = filt_df2[txt].str.lower()
    filt_df2[txt] = filt_df2[txt].str.normalize('NFKD').str.encode('ascii', errors='ignore').\
                str.decode('utf-8')

filt_df2["DT_DISPATCH"] = pd.to_datetime(filt_df2["DT_DISPATCH"]).dt.date
filt_df2.drop(filt_df2[filt_df2["CRIT_CODE"] == 'L'].index, inplace=True)
filt_df2.dropna(subset=["CRIT_CODE"], inplace=True)
filt_df2.drop(filt_df2[filt_df2["INFO_ON_NON_AWARD"].notna() == True].index, inplace=True)
filt_df2["CPV"] = filt_df2["CPV"].astype(str)
filt_df2["main_CPV"] = filt_df2["CPV"].apply(cpv_main_group_extractor)
filt_df2 = filt_df2.drop_duplicates(subset='ID_NOTICE_CAN', keep='first')

#GPP SEARCH FILTERS
lng = "por"
words_to_filter = ["ambiental", "sustentável", "emissão", "poluente", "energia", "renovável"]
variants = []

for words in words_to_filter:
    related = wn.synsets(words, lang=lng)
    for related in related:
        for lemma in related.lemmas(lang=lng):
            variants.extend(lemma.synset().lemma_names(lang=lng))

variants = list(set(variants))
remove = ["programa", "fornecimento", "envio"]
filtered_variants = [word for word in variants if word not in remove]
variants = filtered_variants.copy()
for i in range(len(variants)):
    variants[i] = unidecode(variants[i])

#FILTERING THE DATA PER YEAR BASED ON THE VARIANTS
gpp_ted = list()
total_ted = list()
all_gpp_teds = pd.DataFrame()
groupedFrame = filt_df2.groupby(filt_df2['YEAR'])
entries = list(groupedFrame.groups.keys())
for grp in entries:
    curr_group = groupedFrame.get_group(grp)
    total_ted.append(len(curr_group))
    bool_GPP = curr_group['CRIT_CRITERIA'].str.contains('|'.join(variants), case=False)
    idx_GPP = np.where(bool_GPP == True)
    all_gpp_teds = pd.concat([all_gpp_teds, curr_group.iloc[idx_GPP[0]]])
    gpp_ted.append(len(curr_group.iloc[idx_GPP[0]]))

gpp_to_tender = list()
for year in range(len(entries)):
    gpp_to_tender.append(100*gpp_ted[year]/total_ted[year])
'''
plt.figure(1)
leg = list()
plt.bar(entries, total_ted, width=0.4)
leg.append("Total TEDs of the year")
plt.bar(entries, gpp_ted, width=0.2, color='maroon')
leg.append("GPP oriented TEDs of the year")
plt.xlabel("Number of contracts")
plt.ylabel("Year")
plt.title("GPP oriented TEDs throughout the years 2018-2022")
plt.show()

plt.figure(2)
plt.bar(entries, gpp_to_tender, width=0.4)
plt.xlabel("GPP oriented tenders [%]")
plt.ylabel("Year")
plt.title("Percentage of GPP oriented TEDs throughout the years 2018-2022")
plt.show()
'''

