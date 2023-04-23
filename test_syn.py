from datetime import datetime, timedelta
import numpy as np
from sklearn.svm import OneClassSVM

from util import *
dataRoot1 = 'E:/data/ubicomp2018/release/nyc/'
dataRoot2 = 'C:/Users/fander/Desktop/project/release/synthetic/'
data_o = np.loadtxt(dataRoot2 + "data.txt", dtype=int)
data=data_o[:,0:148]
MID = np.loadtxt(dataRoot2 + "MID.txt", dtype=int) # matrix indicating anomaly of type ID
MTS = np.loadtxt(dataRoot2 + "MTS.txt", dtype=int) # matrix indicating anomaly of type TS
MR = np.loadtxt(dataRoot2+ "MR.txt", dtype=int) # matrix indicating anomaly of type R
MTH = np.loadtxt(dataRoot2 + "MTH.txt", dtype=int) # matrix indicating Rain
MH = np.loadtxt(dataRoot2+ "MH.txt", dtype=int) # matrix indicating Holiday

data=data/100


nR = 148 # number of regions
nS = 2 # number of data sources
MPS = 30 # minutes per time slot, must divides 1440 (minutes of day)
nWeek = 6
nTDay = 60 * 24 // MPS # time slots per day 48
nTWeek = nTDay*7 # time slots per week  336
nT = nTWeek*nWeek # total time slots  2016

lCorr = 60 * 24 *7  // MPS  # use one week data for calculating pearson correlation

tsTrain = 60 * 24 *7  // MPS
detect_st = 60 * 24 * 7 * 4 // MPS#1344=336*4
ed = 60 * 24 * 7 * nWeek // MPS #2016=336*6
st = max(detect_st , lCorr)#1344-336


trained = False
a=0
b=0
c=0
d=0
p1 = np.einsum('ij,ik->kj', data[(st-lCorr):st,:], data[(st-lCorr):st,:])# 336*3448矩阵点积3448*3448
for ts in range(st, ed,1):#1小时一个步长
    #print('\r' + str(ts), end='')
    #6为单个点所占的时间块数量
    # 保存该时间点下的每个区域的异常分数
    #score_ind = np.zeros((1,nR ))
    score_ind_lof=np.zeros([nR])
    for aera_index in range (0,nR):
        score=lof(ts,data,aera_index,1,30,5)
        #score_ind_lof[aera_index]=score
        #if(score>1):
            #print(str(score)+' '+str(aera_index))
        a+=1
        if score>0.50:
            b+=1
            score_ind_lof[aera_index] = score


    pp = np.nan_to_num(pairPearson(data[(ts - lCorr):ts, :], data[(ts - lCorr):ts, :], p1))  # 把一个区域看做一个变量，统计一个区域（变量）内336个time_slot与其他变量的相关性
    print(pp.max())
    p1 = p1 + data[ts, :] * data[ts, :][:, None]
    p1 = p1 - data[ts - lCorr, :] * data[ts - lCorr, :][:, None]
    pp_old = np.nan_to_num(pairPearson(data[(ts - lCorr -1):(ts -1), :], data[(ts - lCorr -1):(ts -1), :], p1))
    pp_diff = pp_old-pp
    #pp_diff[pp_diff<0]=0
   # pp_diff[np.where(np.logical_or(pp < 0.92, pp_diff < 0))]=0
    pp_diff [np.where(np.logical_or(pp_old < 0.95, pp_diff < 0))] = 0#相关系数小于阈值或者相关系数增加
    #pp_diff[pp < 0.8] = 0
  #  score_ind=np.sum(pp_diff,axis=1)
    pp_tmp = np.array(pp_old)
    pp_tmp[np.where(pp_old < 0.95)] = 0
    score_ind_pcc=  np.nan_to_num(np.sum(pp_tmp * pp_diff, axis=1) / np.sum(pp_tmp, axis=1))
 #score_ind[ts, :] =np.nan_to_num(np.sum(pp_tmp * pp_diff, axis=1) / np.sum(pp_tmp, axis=1))

    score_ind_pcc[np.where(score_ind_pcc<0)] = 0  # 相关系数小于阈值或者相关系数增加
    score_ind_pcc[np.where(score_ind_pcc > 1)] = 1
    max_lof_temp=score_ind_lof.max()
    max_lof=min(max_lof_temp,15)
    max_pcc=score_ind_pcc.max()
    #print(max_lof)
    print(max_pcc)
    score_final=score_ind_pcc*50+score_ind_lof
    """
    score_sort_lof=np.argsort(np.argsort(score_ind_lof))
    score_sort_pcc=np.argsort(np.argsort(score_ind_pcc))
    #获得每个区域的异常得分
    #score_sort_final2 = score_sort_lof*0.5 + score_sort_pcc
   #获得异常得分的排名，数组的元素代表区域索引，数组的索引代表的是异常程度
    score_sort_final = np.argsort(np.argsort( score_sort_lof*2+ score_sort_pcc))
    """
    score_sort_final = np.argsort(np.argsort(score_final))
    anomaly=MTS[ts,:]
    #sum1=np.sum(anomaly,axis=0)
    #print(score_ind)
    #mask=pp>0.90
    idx = np.array(np.where(anomaly == 1))
    if  np.size(idx)==1:
        #print(idx[0])
        c+=1
        #print(score_sort_final[idx[0]])
        if  score_sort_final[idx[0]]>100:
            d+=1
        #print(' ')


    #count=np.sum(mask,axis=1)
    #print(count)
print(c)
print(d)
