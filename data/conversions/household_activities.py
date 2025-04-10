import numpy as np
import pickle

dist_HH = np.array([[1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0.28,0,0.72,0],
                    [1,0,0,0,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0.03,0,0,0.97,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [0,1,0,0,0],
                    [0,0,0,1,0],
                    [0,1,0,0,0],
                    [0,1,0,0,0],
                    [0,0.28,0,0.72,0],
                    [0,0.28,0,0.72,0],
                    [0,1,0,0,0],
                    [0,1,0,0,0],
                    [0,0.78,0,0.22,0],
                    [0,1,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,0,0,0],
                    [0,0,1,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0.5,0.07,0.24,0.12],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0.21,0.12,0.67,0],
                    [0,0.48,0,0.52,0],
                    [0,0.48,0,0.52,0],
                    [0,0.48,0,0.52,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,0,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0.63,0,0.36,0],
                    [0,0.3,0,0.08,0],
                    [0,1,0,0,0],
                    [0,0,0.04,0.91,0],
                    [0,1,0,0,0],
                    [0,0.41,0,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0.38,0,0.62,0],
                    [0,0,0,1,0],
                    [0,1,0,0,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0.34,0.26,0,0.4,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0,0,0,0],
                    [0,0.03,0,0.97,0],
                    [0,0.03,0,0.97,0],
                    [0,0.6,0,0.4,0],
                    [0,0.6,0,0.4,0],
                    [0,0,0,1,0],
                    [0,0,0,1,0],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,1,0,0],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [1,0,0,0,0],
                    [0,0.94,0,0.06,0],
                    [0,0.01,0.04,0.94,0],
                    [0,0.59,0.01,0.4,0],
                    [0,0.92,0,0.08,0],
                    [0,0.07,0,0.93,0],
                    [0,0.46,0.05,0.38,0],
                    [1,0,0,0,0],
                    [0,1,0,0,0],
                    [1,0,0,0,0],
                    [1,0,0,0,0],
                    [0,0.05,0,0.96,0],
                    [1,0,0,0,0],
                    [0,0,0,1,0],
                    [1,0,0,0,0],
                    [0,0.94,0,0.06,0],
                    [0,0.2,0.03,0.75,0],
                    [0,0.53,0.02,0.42,0],
                    [0,0.92,0,0.08,0],
                    [0,0.3,0,0.7,0],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,1],
                    [0,0,0,0,0],
                    [0,0,0,0,0]])

path = "C:/Users/yamad/OneDrive/Documentos/FORCERA/GPP/GPP-data-inspection/data/conversions/"
np.save(path+'conv_HH',dist_HH)
