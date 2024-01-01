from datetime import datetime, timedelta
import numpy as np
import pandas as pd
file_path2='anomalies3.txt'
#df2 = pd.read_csv(file_path2,header=None)
data_np = np.loadtxt('anomalies.txt')#, delimiter='\t')
num=0
num2=0
for row in data_np:
    for element in row:
        num2+=1
        if int(element)==1:
            num+=1
print(num2)
print(num)

current_time=(datetime.now())
formatted_time = current_time.strftime("%Y-%m-%d-%H-%M-%S")
print(formatted_time+'_'+"anomalies11.txt")#, anomalies) # detected anomalies
np.savetxt( formatted_time+'_'+"anomalies11.txt", 'a')