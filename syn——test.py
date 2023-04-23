from datetime import datetime, timedelta
import numpy as np
from sklearn.svm import OneClassSVM

from util import *

# dataRoot = "path_for_synthetic_data"
dataRoot1 = 'E:/data/ubicomp2018/release/nyc/'
dataRoot2 = 'C:/Users/fander/Desktop/project/release/synthetic/'
# C:/Users/fander/Desktop/project/release/nyc/
data = np.loadtxt(dataRoot2 + "data.txt", dtype=int)
MID = np.loadtxt(dataRoot2 + "MID.txt", dtype=int)  # matrix indicating anomaly of type ID
MTS = np.loadtxt(dataRoot2 + "MTS.txt", dtype=int)  # matrix indicating anomaly of type TS
MR = np.loadtxt(dataRoot2 + "MR.txt", dtype=int)  # matrix indicating anomaly of type R
MTH = np.loadtxt(dataRoot2 + "MTH.txt", dtype=int)  # matrix indicating Rain
MH = np.loadtxt(dataRoot2 + "MH.txt", dtype=int)  # matrix indicating Holiday

dists = np.loadtxt(dataRoot2 + "dists.txt")  # pairwise distance between regions

# scale down the data for calculating pearson correlation
data = data / 100

nR = 148  # number of regions
nS = 2  # number of data sources
MPS = 30  # minutes per time slot, must divides 1440 (minutes of day)
nWeek = 6
nTDay = 60 * 24 // MPS  # time slots per day
nTWeek = nTDay * 7  # time slots per week
nT = nTWeek * nWeek  # total time slots

# Params for algorithm
alpha = 0.01
beta = 0.05
nDailyAnomaly_int = int(60 / MPS * 24 * nR * alpha)
nDailyAnomaly_r = int(60 / MPS * 24 * nR * beta)
t_delta = 2
corrThres = 0.9
lCorr = 60 * 24 * 7 // MPS  # use one week data for calculating pearson correlation
R = 800

nNearPart = 2

# 128*128的对角矩阵
mNear = np.identity(nR)  # 128*128

# 在0轴方向进行拼接，相对于148行之后代表了周边邻接信息
mNear = np.concatenate((mNear, (dists > 0) & (dists <= R)))  # 296*148

# 相对于将mNear.sum数组水平方向上复制了4次，而且是一个一个复制
sMNear = np.repeat(mNear.sum(axis=1), nS * t_delta)  # 1184*1=4*296

mNearTile = np.tile(mNear, (1, nS * t_delta))  # 296*(148*4)

score_ind = np.zeros((nT, nR * nS))

score_r = np.zeros((nT, nR)) + 100
score_lof=np.zeros((nT, nR)) + 100

score_int = np.zeros((nT, nR)) + 100
anomalies = np.zeros((nT, nR))
anomalies2=np.zeros((nT, nR))
dVector = (t_delta - 1 + nNearPart) * nS

model_r = OneClassSVM(nu=0.1)
model_int = OneClassSVM(nu=0.1)
train_r = np.zeros((0, nS))
train_int = np.zeros((0, dVector))
tsTrain = 60 * 24 * 7 // MPS
nTrain = tsTrain * nR

detect_st = 60 * 24 * 7 * 4 // MPS
ed = 60 * 24 * 7 * nWeek // MPS
st = max(detect_st - tsTrain, lCorr)

trained = False
#qwe
c=0
d=0
a=0
b=0
e=0
p1 = np.einsum('ij,ik->kj', data[(st - lCorr):st, :], data[(st - lCorr):st, :])
for ts in range(st, ed):

    score_ind_lof=np.zeros([nR])
    for aera_index in range (0,nR):
        score=lof(ts,data[:,0:nR],aera_index,2,30,5)
        score_ind_lof[aera_index]=score
      #  if(score>1):
            #print(str(score)+' '+str(aera_index))
        a+=1
        if score>1.0:
            b+=1
            score_lof[ts:aera_index] = score

    print('\r' + str(ts), end='')
    pp = np.nan_to_num(pairPearson(data[(ts - lCorr):ts, :], data[(ts - lCorr):ts, :], p1))
    p1 = p1 + data[ts, :] * data[ts, :][:, None]
    p1 = p1 - data[ts - lCorr, :] * data[ts - lCorr, :][:, None]
    pp_new = np.nan_to_num(pairPearson(data[(ts - lCorr + 1):(ts + 1), :], data[(ts - lCorr + 1):(ts + 1), :], p1))
    pp_diff = pp - pp_new
    pp_diff[np.where(np.logical_or(pp < corrThres, pp_diff < 0))] = 0
    pp_diff = pp_diff * lCorr
    pp_tmp = np.array(pp)
    pp_tmp[np.where(pp < corrThres)] = 0

    scaledData = ((data[:(ts + 1), :] - data[:(ts + 1), :].mean(0)) / data[:(ts + 1), :].std(0))[-1]
    weightedAvg = np.nan_to_num(
        np.sum(pp_tmp * np.tile(scaledData, (scaledData.shape[0], 1)), axis=1) / np.sum(pp_tmp, axis=1))
    sign = ((scaledData > weightedAvg).astype(int) - 0.5) * 2
    score_ind[ts, :] = sign * np.nan_to_num(np.sum(pp_tmp * pp_diff, axis=1) / np.sum(pp_tmp, axis=1))
    # score_ind[(ts-t_delta+1):(ts+1),:].ravel()   592*1
    # mNearTile=296*592 水平方向上是相等的4份
    # 1184*148→1184*1
    tmpX = (mNearTile * score_ind[(ts - t_delta + 1):(ts + 1), :].ravel()).reshape((-1, nR)).sum(axis=1)
    tmpX = np.nan_to_num(tmpX / sMNear)
    tmpX = tmpX.reshape(nNearPart, nR, t_delta, nS).transpose([1, 2, 0, 3]).reshape((nR, -1))  # 148*8

    #     tmpX[:,-nS*nNearPart:]tmpX的后四列、
    #  tmpX[:,:-nS*nNearPart]除了后四列的所有列
    # (nR,t_delta-1,nNearPart,nS)=(148,1,2,2)

    tmpX = np.c_[tmpX[:, -nS * nNearPart:], tmpX[:, :-nS * nNearPart].reshape((nR, t_delta - 1, nNearPart, nS))[:, :, 0,    :].reshape((nR, -1))]
    x_r = np.array(tmpX[:, 0:nS])  # 148*2
    #x_int = np.array(tmpX)  # 148*6

    train_r = np.r_[train_r, x_r][-nTrain:, :]  # 不断拼接
    #train_int = np.r_[train_int, x_int][-nTrain:, :]

    if ts > detect_st:
        if  ts % (14*60 / MPS * 24) == 0 or not trained:# or
            #if not trained:
            model_r.fit(train_r)
           # model_int.fit(train_int)
            trained = True

        # 输出异常得分
        score_r[ts, :] = model_r.decision_function(x_r).flatten()  # score_r = 2016*148
        argsort_lof=score_lof[(ts - 60 * 24 // MPS + 1):(ts + 1), :].flatten().argsort()
        #argsort_lof = argsort_lof[0:100]
        #iAnomalies2 = argsort_lof[(argsort_lof // nR) == (60 * 24 // MPS - 1)] % nR
        #anomalies2[ts,iAnomalies2]=1

        #score_int[ts, :] = model_int.decision_function(x_int).flatten()  # 2016*148
        argsort_r = score_r[(ts - 60 * 24 // MPS + 1):(ts + 1), :].flatten().argsort()  # (148*48) 1day*148zones  一天的异常数
        #argsort_int = score_int[(ts - 60 * 24 // MPS + 1):(ts + 1), :].flatten().argsort()  # 148*48 1day*148zones
        # 返回int第几个元素是在r中的
        #selected_int = argsort_int[np.where (np.in1d(argsort_int, argsort_r[0:nDailyAnomaly_r])) [0]][  0:nDailyAnomaly_int]  # 71of355 #where函数的作用是寻找int数组中在_r数组中对应下标
        # 输出异常区域id

        final = argsort_lof[np.where (np.in1d(argsort_lof, argsort_r[0:100])) [0]][0:100]
       #iAnomalies = argsort_r[(argsort_r // nR) == (60 * 24 // MPS - 1)]
        #iAnomalies = argsort_r[(argsort_r // nR) == (60 * 24 // MPS - 1)] % nR
        iAnomalies = final[(final // nR) == (60 * 24 // MPS - 1)] % nR
        #print(len(np.unique( iAnomalies)))
        iAnomalies = iAnomalies[score_r[ts, iAnomalies] != 100]
        anomalies[ts, iAnomalies] = 1

        argsort_r = argsort_r[0:100]
        iAnomalies2 = argsort_r[(argsort_r // nR) == (60 * 24 // MPS - 1)] % nR
        iAnomalies2 = iAnomalies2[score_r[ts, iAnomalies2] != 100]
        anomalies2[ts,iAnomalies2]=1



        anomaly = MTS[ts, :]
        idx = np.array(np.where(anomaly == 1))
        if      np.size(idx)==1:
            c+=1
        #print(score_sort_final[idx[0]])
            if anomalies[ts,idx[0]]==1:
                d+=1
            if anomalies2[ts,idx[0]]==1:
                e+=1
        #print(' ')
#np.savetxt(dataRoot2 + "anomalies.txt", anomalies)  # detected anomalies
print(c)
print(d)
print(e)