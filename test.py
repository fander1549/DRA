from datetime import datetime, timedelta
import numpy as np
from sklearn.svm import OneClassSVM

from util import *
dataRoot1 = 'E:/data/ubicomp2018/release/nyc/'
dataRoot2 = 'C:/Users/fander/Desktop/project/release/nyc/'
data_o = np.loadtxt(dataRoot2 + 'taxi.txt')#(351days*48times)*(2*862zones)
data=data_o[:,0:862]
nR = 862 # number of regions
nS = 2# number of data sources
MPS = 30 # minutes per time slot
nT = data.shape[0] # nummber of time slots
stDT = datetime(2014,1,15,0,0,0)

detect_st = (datetime(2014,11,5) - stDT).days * 24 * 60 // MPS  # detect anomamlies in 2014-11-27，stTD为开始日期，一年中的第一个星期作为基准
ed = (datetime(2014,11,20) - stDT).days * 24 * 60 // MPS

tsTrain = 60 * 24 * 7 // MPS
lCorr = 60 * 24 *7  // MPS  # use one week data for calculating pearson correlation
st = max(detect_st - tsTrain, lCorr)
#st=detect_st

trained = False
a=0
b=0
p1 = np.einsum('ij,ik->kj', data[(st-lCorr):st,:], data[(st-lCorr):st,:])# 336*3448矩阵点积3448*3448
for ts in range(st, ed,6):#三小时一个步长
    #print('\r' + str(ts), end='')
    #6为单个点所占的时间块数量
    # 保存该时间点下的每个区域的异常分数
    #score_ind = np.zeros((1,nR ))
    score_ind_lof=np.zeros([862])
    for aera_index in range (0,nR):
        score=lof(ts,data,aera_index,6,30,5)
        score_ind_lof[aera_index]=score
        #if(score>1):
            #print(str(score)+' '+str(aera_index))
        a+=1
        if score>1.5:
            b+=1

    pp = np.nan_to_num(pairPearson(data[(ts - lCorr):ts, :], data[(ts - lCorr):ts, :], p1))  # 把一个区域看做一个变量，统计一个区域（变量）内336个time_slot与其他变量的相关性
    p1 = p1 + data[ts, :] * data[ts, :][:, None]
    p1 = p1 - data[ts - lCorr, :] * data[ts - lCorr, :][:, None]
    pp_old = np.nan_to_num(pairPearson(data[(ts - lCorr -6):(ts -6), :], data[(ts - lCorr -6):(ts -6), :], p1))
    pp_diff = pp_old-pp
    #pp_diff[pp_diff<0]=0
   # pp_diff[np.where(np.logical_or(pp < 0.92, pp_diff < 0))]=0
    pp_diff [np.where(np.logical_or(pp_old < 0.9, pp_diff < 0))] = 0#相关系数小于阈值或者相关系数增加
    #pp_diff[pp < 0.8] = 0
  #  score_ind=np.sum(pp_diff,axis=1)
    pp_tmp = np.array(pp_old)
    pp_tmp[np.where(pp_old < 0.95)] = 0
    score_ind_pcc=  np.nan_to_num(np.sum(pp_tmp * pp_diff, axis=1) / np.sum(pp_tmp, axis=1))
    print(max(score_ind_pcc))

    score_sort_lof=np.argsort(np.argsort(score_ind_lof))
    score_sort_pcc=np.argsort(np.argsort(score_ind_pcc))
    #获得每个区域的异常得分
    score_sort_final2 = score_sort_lof*0.5 + score_sort_pcc
   #获得异常得分的排名，数组的元素代表区域索引，数组的索引代表的是异常程度
    score_sort_final = np.argsort(np.argsort( score_sort_lof*0.5+ score_sort_pcc))
    #print(score_ind)
    #mask=pp>0.90
    x=1
    #count=np.sum(mask,axis=1)
    #print(count)
print(b/a)
