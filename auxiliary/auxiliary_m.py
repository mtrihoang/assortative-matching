#!/usr/bin/env python
# coding: utf-8

# In[ ]:

#%%

import pandas as pd 
import geopandas as gpd
from geopandas import GeoDataFrame as gdf
import matplotlib.pyplot as plt
import seaborn as sns 

'''map'''
def frmap(department, france):
    mortality = department[department["post"] == 1]
    merged = mortality.merge(france, left_on='depc', right_on='ID_2', how = 'outer')[['depc', 'NAME_2', 'mortality', 'geometry']]
    df = gpd.GeoDataFrame(merged)
    department = df['NAME_2'].unique()
    df['coords'] = df['geometry'].apply(lambda x: x.representative_point().coords[:])
    df['coords'] = [coords[0] for coords in df['coords']]
    fig, ax = plt.subplots(1, figsize=(14,14))
    ax.axis('off')
    bx = df.plot(column='mortality', ax=ax,linewidth=1, scheme='UserDefined', edgecolor='black', alpha=1, 
    classification_kwds={'bins':[12.08107, 16.32464, 17.45, 17.6, 19.5]}, legend=True)
    for xy, label in zip(df['coords'], df['NAME_2']):
        bx.annotate(label, xy= xy, xytext=(1, 1), textcoords="offset points", fontsize = 8, weight = 600,
        bbox=dict(boxstyle="round", fc="w"))


'''figures'''
def mdist_hue(d, varlist, nrows, ncols):

    df = d.copy()
    i = 0
    j = 0
    sns.set_style('ticks')
    fig, axs = plt.subplots(nrows=nrows, ncols = ncols)
    fig.set_size_inches(15, 10)
    for var in varlist:
        df[var] = pd.to_numeric(df[var], downcast='integer')
        sns.histplot(data=df, x=var, hue="post", element="bars", stat="probability", 
                     binwidth = 1, discrete=True, ax = axs[i,j])
        if j > (ncols -2):
            i = 1
            j = -1
        j += 1
        
def mdist_hue_bin(d, varlist, nrows, ncols, binwidth):

    df = d.copy()
    i = 0
    j = 0
    sns.set_style('ticks')
    fig, axs = plt.subplots(nrows=nrows, ncols = ncols)
    fig.set_size_inches(15, 10)
    for var in varlist:
        df[var] = pd.to_numeric(df[var], downcast='integer')
        sns.histplot(data=df, x=var, hue="post", element="step", stat="probability", 
                     binwidth = binwidth, common_norm=False, ax = axs[i,j])
        if j > (ncols -2):
            i = 1
            j = -1
        j += 1
        
def mdist_hue_nobin(d, varlist, nrows, ncols):

    df = d.copy()
    i = 0
    j = 0
    sns.set_style('ticks')
    fig, axs = plt.subplots(nrows=nrows, ncols = ncols)
    fig.set_size_inches(15, 10)
    for var in varlist:
        df[var] = pd.to_numeric(df[var], downcast='integer')
        sns.histplot(data=df, x=var, hue="post", element="step", stat="probability", common_norm=False, ax = axs[i,j])
        if j > (ncols -2):
            i = 1
            j = -1
        j += 1
        
def mdist_nohue(d, varlist, nrows, ncols):

    df = d.copy()
    i = 0
    j = 0
    sns.set_style('ticks')
    fig, axs = plt.subplots(nrows=nrows, ncols = ncols)
    fig.set_size_inches(15, 10)
    for var in varlist:
        sns.histplot(data=df, x=var, element="step", stat="probability", common_norm=False, ax = axs[i,j])
        if j > (ncols -2):
            i = 1
            j = -1
        j += 1


'''Extension: table 3'''
def ext_3(d):
    df3 = d.copy()
    df3_1 = df3[df3['clgr']>=3]
    sns.set_theme(style="darkgrid", palette='deep')
    sns.lmplot(x = "post_mortality", y = "classdiff", col="rural", hue = 'rural', palette="Set1", data = df3)
    sns.lmplot(x = "post_mortality", y = "classdiff", col="rural", hue = 'rural', palette="Set1", data = df3_1)


# %%
