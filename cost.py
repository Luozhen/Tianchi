#! user/bin/env python
# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import processtime as ps

data = pd.read_csv(r'./resource/sample_submission.csv',
                   names=['Counter_id', 'Addr', 'Arrival_time', 'Departure', 'Amount', 'Order_id'])  # 读取表格
site = pd.read_csv(r'./resource/1.csv',
                   names=['Site_id', 'lng', 'lat']).drop(0)
spot = pd.read_csv(r'./resource/2.csv',
                   names=['Spot_id', 'lng', 'lat']).drop(0)
shop = pd.read_csv(r'./resource/3.csv',
                   names=['Shop_id', 'lng', 'lat']).drop(0)
shopOrder = pd.read_csv(r'./resource/5.csv',
                   names=['Order_id', 'Spot_id', 'Shop_id', 'Pickup_time', 'Delivery_time', 'Num']).drop(0)

def isSiteAddr(addr):
    if not site['Site_id'][site['Site_id'] == addr].empty:
        return True
    return False

def isSpotAddr(addr):
    if not spot['Spot_id'][spot['Spot_id'] == addr].empty:
        return True
    return False

def isShopAddr(addr):
    if not shop['Shop_id'][shop['Shop_id'] == addr].empty:
        return True
    return False

def lngAndLat(addr):   # 将str地点转换成具体经纬度
    if isSiteAddr(addr):
        return site[['lng', 'lat']][site['Site_id'] == addr]
    elif isSpotAddr(addr):
        return spot[['lng', 'lat']][spot['Spot_id'] == addr]
    elif isShopAddr(addr):
        return shop[['lng', 'lat']][shop['Shop_id'] == addr]

def assume7(addr1, addr2):   # 假设7 两个地点的配送时间
    ds1 = lngAndLat(addr1)
    ds2 = lngAndLat(addr2)
    lat1 = float(np.array(ds1['lat'])[0])
    lng1 = float(np.array(ds1['lng'])[0])
    lat2 = float(np.array(ds2['lat'])[0])
    lng2 = float(np.array(ds2['lng'])[0])
    return ps.getttime(lat1,lng1,lat2,lng2)


def assume8(data, num):   # 假设8 成立条件
    ptime = ps.getptime(num)
    time = data['Departure'] - data['Arrival_time']
    if abs(ptime - time) < 1:
        return True
    return False

def findO2Orders(data):   # 对每个配送员配送方案 查找O2O订单
    orders = []
    for i in data.index:
        row = data.loc[i]
        if row[0] == 'E':
            orders.append(i)
    return list(set(orders))

def timeTrans(time):   # 时间偏移转换
    timeList = time.split(':')
    hour = int(timeList[0])
    minute = int(timeList[1])
    return (hour - 8) * 60 + minute

def rArrivefDep(order):   # O2O商家规定订单取/送时间
    time = shopOrder[['Pickup_time', 'Delivery_time']][shopOrder['Order_id'] == order]
    pickTStr = np.array(time)[0][0]
    deliverTStr = np.array(time)[0][1]
    return timeTrans(pickTStr), timeTrans(deliverTStr)


def O2OTimeDiff(data):   # 配送员超过的O2O商家预定时间
    time = 0
    O2Orders = findO2Orders(data)
    for od in O2Orders:
        otpInfo = data[['Addr', 'Arrival_time', 'Departure']][data['Order_id'] == od]
        rfetchT, rarriveT = rArrivefDep(od)   # 商家规定取/送时间
        pfetchT = otpInfo.iloc[0]['Arrival_time']
        parriveT = otpInfo.iloc[1]['Arrival_time']
        time += (pfetchT - rfetchT) + (parriveT - rarriveT)
    return time


totalTime = 0
for attri, subdata in data.groupby(data['Counter_id']):
    minArrive = min(subdata['Arrival_time'])
    maxDeparture = max(subdata['Departure'])
    totalTime += (maxDeparture - minArrive)
    preRow = subdata.iloc[0]
    for i in subdata.index:
        row = subdata.loc[i]
        if row['Amount'] < 0 and (not assume8(row, -row['Amount'])):
            totalTime += int(abs(row['Departure'] - row['Arrival_time'] - ps.getptime(-row['Amount']))) * 10
        timeDiff = assume7(preRow['Addr'], row['Addr'])
        preDepart = preRow['Departure']
        nowArrive = row['Arrival_time']
        if not (abs(nowArrive - preDepart - timeDiff) < 1):
            totalTime += int(abs(nowArrive - preDepart - timeDiff)) * 10
        preRow = row
    totalTime += O2OTimeDiff(subdata) * 5

print totalTime