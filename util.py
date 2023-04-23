import numpy as np
import math

def pairPearson(A, B, precompute_p1):
    # Get number of rows in either A or B
    N = B.shape[0]
    #A=B=data[(st - lCorr):st, :]
    # Store columnw-wise in A and B, as they would be used at few places
    #相当于将矩阵纵向求和压缩
    sA = A.sum(0)
    sB = B.sum(0)

    # Basically there are four parts in the formula. We would compute them one-by-one
    p1 = N*precompute_p1#1724*1724
    #将sB进行转置，同时利用广播机制
    p2 = sA*sB[:,None]#1724*1724
    p3 = N*((B**2).sum(0)) - (sB**2)#1724*1
    p4 = N*((A**2).sum(0)) - (sA**2)#1724*1

    # Finally compute Pearson Correlation Coefficient as 2D array 
    #None为追加维度
    pcorr = ((p1 - p2)/np.sqrt(p4*p3[:,None]))#3448*3448
    pcorr[np.isinf(pcorr)] = 0
    pcorr[np.isnan(pcorr)] = 0
    return pcorr
#传入一个数据点，总数据，单个数据点所包含的slot数量以及slot的长度

def BhattacharyyaFlow(data,aera_index,point_a,point_b,time_slots_dectected):
    distance =0.0
    for i in range(0,time_slots_dectected):
        distance = distance + (data[point_a-i][aera_index] -data[point_b-i][aera_index])**2
    d = np.sqrt(distance);
    return (d);
#def lrd():

def Knn_point(point_o ,data,aera_index,time_slots_dectected,time_slot_length,Knn_n):
    KNN = np.empty((14))
    step_size = int(24 * 60 / time_slot_length)
    point_a = point_o
    for i in range(1, 15):
        point_b = point_o - step_size*i
        KNN[i-1] = BhattacharyyaFlow(data, aera_index, point_a, point_b, time_slots_dectected)
    min_indexes = np.argpartition(KNN, Knn_n)[:Knn_n]
    #返回最近点的索引
    return min_indexes

def lrd_disatance (point_o ,data,aera_index,time_slots_dectected,time_slot_length,Knn_n):
    distance=0
    step_size = int(24 * 60 / time_slot_length)
    min_point_indexes=Knn_point(point_o ,data,aera_index,time_slots_dectected,time_slot_length,Knn_n)
    #根据最近点的索引计算lrd距离
    for i in range(0,Knn_n):
        point_temp=point_o-step_size*(min_point_indexes[i]+1)
        distance+=BhattacharyyaFlow(data,aera_index,point_o,point_temp,time_slots_dectected)
    if distance!=0:
        distance=Knn_n/distance
    return distance

def lof(point_o ,data,aera_index,time_slots_dectected,time_slot_length,Knn_n):
    #往前推两个两个星期，从半个月中找出离得最近的若干点
    score=0
    step_size = int(24 * 60 / time_slot_length)
    min_point_indexes=    Knn_point(point_o ,data,aera_index,time_slots_dectected,time_slot_length,Knn_n)
    LOF_distance_a=lrd_disatance(point_o,data,aera_index,time_slots_dectected,time_slot_length,Knn_n)
    LOF_distance_b=0
    for i in range(0,Knn_n):
        point_temp=point_o-step_size*(min_point_indexes[i]+1)
        LOF_distance_b+=lrd_disatance(point_temp,data,aera_index,time_slots_dectected,time_slot_length,Knn_n)
    if LOF_distance_a!=0:
        score=LOF_distance_b/(LOF_distance_a*Knn_n)

    #print(score)
    return score

