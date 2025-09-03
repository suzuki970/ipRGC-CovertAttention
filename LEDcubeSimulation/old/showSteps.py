#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 18:16:26 2023

@author: yutasuzuki
"""


import json
import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()
sns.set(font_scale=1.5)
sns.set_style("whitegrid")
sns.set_palette("Set2")

fName = "data_LEDCube_20230318x30y26"

files = glob.glob(fName + "*.json")
files.sort(reverse=True)

dat = pd.DataFrame()
for i,fName in enumerate(files):
    f = open(fName)
    resAll = json.load(f)
    f.close()

    tmp = pd.DataFrame(
        np.array(resAll["Lab"])[:,1:],
        # np.array(resAll["Yxy"])[:,1:],
        columns=["x","y"])
    if i == 0:
        tmp["steps"] = "plus"
    
    else:
        tmp["steps"] = fName.split('.')[0][-5:]
    
    dat = pd.concat([dat,tmp])


plt.figure()
sns.scatterplot(x="x", y="y", hue="steps",data=dat[dat["steps"]!="plus"], alpha=0.4)
sns.scatterplot(x="x", y="y", hue="steps",data=dat[dat["steps"]=="plus"])

plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)


resAll["L-M contrast"]=[]
resAll["S-(L+M) contrast"]=[]

for i,lms in enumerate(resAll["LMS"]):
    resAll["L-M contrast"].append(np.round(lms[0]-lms[1],5))
    resAll["S-(L+M) contrast"].append(np.round(lms[2]-(lms[1]+lms[0]),5))

plt.figure()    
for (ml,lm_s) in zip(resAll["L-M contrast"],resAll["S-(L+M) contrast"]):
    plt.plot(ml,lm_s,'o')
plt.plot(resAll["L-M contrast"][0],resAll["S-(L+M) contrast"][0],'ro',markersize=10)
    
plt.xlabel("L-M contrast(green-red)")
plt.ylabel("S-(L+M) contrast(yellow-blue)")