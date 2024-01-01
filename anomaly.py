from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM
file_path='/Users/rfande/PycharmProjects/DRA/yicahng——data.csv'
file_path='yicahng——data2.csv'
file_path2='2024-01-04-23-45-10_anomalies11.txt'
df = pd.read_csv(file_path,header=None)#,names=['a', 'b', 'b','d','e','f'])#, skiprows=2)
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
count=0
count2=0
for i in range (0,len(df)):
    item=df.iloc[i]
    zone_id1=item[2]
    zone_id2=item[3]
    start_time=item[4]
    start_time = pd.to_datetime(start_time ,format='%Y/%m/%d %H:%M')
    end_time=item[5]
    end_time = pd.to_datetime(end_time, format='%Y/%m/%d %H:%M')
    stDT =  pd.to_datetime('2014/1/15 00:00', format='%Y/%m/%d %H:%M')
    #timestamp1 = pd.Timestamp(datetime(2022, 1, 1, 10, 0, 0))
    #timestamp2 = pd.Timestamp(datetime(2022, 1, 1, 12, 30, 0))
    # 直接计算相差的分钟数
    minutes_difference = (end_time - stDT).total_seconds()//60
    start_index=int((start_time- stDT).total_seconds()//1800)
    end_index=int((end_time - stDT).total_seconds()//1800)

    #print(start_index)
   # print(end_index-start_index)
    #print(zone_id1)
    for i in range(start_index-1,end_index+1):
        #print(int(data_np[i][zone_id1]))
        #print(data_np[i][zone_id1-1])
        if int(data_np[i][zone_id1])==1 :
            count+=1
            break
    for i in range(start_index-1,end_index+1):

        if zone_id2>=0:
            if  int (data_np[i][int(zone_id2)]==1):
                count2+=1
                break
print(count)
print(count2)
current_time=(datetime.now())
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
print("当前时间：", current_time)
   # detect_st = (datetime(2014, 11,      27) - stDT).days * 24 * 60 // MPS  # detect anomamlies in 2014-11-27，stTD为开始日期，一年中的第一个星期作为基准
    #ed = (datetime(2014, 11, 28) - stDT).days * 24 * 60 // MPS  # 表示结束时间的索引 -stDT是因为起始时间不是一月一号

