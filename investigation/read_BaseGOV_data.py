import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/"
file = "contratos2022.csv"

raw_hist_data = pd.DataFrame()
years = np.arange(2012, 2023, 1)
for yr in years:
    curr_df = pd.read_csv(path + f'contratos{yr}.csv', sep=',')
    raw_hist_data = pd.concat([raw_hist_data, curr_df], ignore_index=True)

for clm in raw_hist_data.columns:
    if pd.isnull(raw_hist_data[clm]).all():
        raw_hist_data.drop(clm, axis=1, inplace=True)