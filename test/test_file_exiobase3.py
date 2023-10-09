import numpy as np
from framework import file_exiobase3

EB = file_exiobase3.EXIOfiles('PT')
exio = EB.read()
#EB.StructAlgebra()

PT_idx = list()
for idx in range(len(exio.A.index)):
    if (exio.A.index[idx])[0] == 'PT':
        PT_idx.append(idx)

PT_clm_idx = list()
for clm_idx in range(len(exio.Y.columns)):
    if (exio.Y.columns[clm_idx])[0] == 'PT':
        PT_clm_idx.append(clm_idx)



