#! user/bin/env python
# -*- coding:utf-8 -*-
# import numpy as np
import pandas as pd


data = pd.read_csv(r'./resource/sample_submission.csv',
                    names = ['Counter_id', 'Addr', 'Arrival_time', 'Departure', 'Amount', 'Order_id'])   # 读取表格

counters = set(data['Counter_id'])
totalTime = 0
for pers in counters:
    minArrive = min(data['Arrival_time'][data['Counter_id'] == pers])
    maxDeparture = max(data['Departure'][data['Counter_id'] == pers])
    totalTime += (maxDeparture - minArrive)
print totalTime