from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM
file_path='/Users/rfande/PycharmProjects/DRA/yicahng——data.csv'
df = pd.read_csv(file_path)#, skiprows=2)

print (df)