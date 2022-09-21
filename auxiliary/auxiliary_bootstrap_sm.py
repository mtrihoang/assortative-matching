import pandas as pd 
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.transforms as mtransforms

def bootstrap_sm(df, clgr, clbr):
    df = df[df['year']<=1914][[clgr, clbr]].dropna()
    df[clgr] = pd.to_numeric(df[clgr], downcast='integer')
    df[clbr] = pd.to_numeric(df[clbr], downcast='integer')
    df['dist'] = df[clbr] - df[clgr]

    col_name = np.arange(-6, 7).tolist()
    df_bs = pd.DataFrame(columns=col_name, index=range(1000)).fillna(0)

    np.random.seed(547543680)
    for j in range (1, 1001):
        y = pd.DataFrame(np.arange(-6, 7))
        y.columns = ['value']
        gr = np.random.choice(df[clgr], size=len(df), replace=True)
        br = np.random.choice(df[clbr], size=len(df), replace=True)
        dist = br - gr
        (unique, counts) = np.unique(dist, return_counts=True)
        frequencies = np.asarray((unique, counts)).T
        x = pd.DataFrame(frequencies,index=frequencies[:,0])
        x.columns = ['value', 'freq']
        z = y.merge(x, left_on='value', right_on='value', how = 'left')
        z = z.fillna(0)
        col_sum = z['freq'].sum()
        df_bs.iloc[j-1] = z['freq']/(col_sum)*100

    df_bs = df_bs.fillna(0)
    
    for col in df_bs:
        df_bs[col] = df_bs[col].sort_values(ignore_index=True)
    
    df_bs_bound = df_bs.iloc[[math.floor(1000/40), math.floor(39*1000/40)+1]]
    df_bs_bound = df_bs_bound.T
    df_bs_bound['value'] = df_bs_bound.index

    (unique, counts) = np.unique(df['dist'], return_counts=True)
    frequencies = np.asarray((unique, counts)).T
    x1 = pd.DataFrame(frequencies,index=frequencies[:,0])
    x1.columns = ['value', 'actual']
    x1['actual'] = x1['actual']/(x1['actual'].sum())*100

    df_bs_sim = df_bs_bound.merge(x1, left_on='value', right_on='value', how = 'left')
    df_bs_sim = df_bs_sim.fillna(0)
    df_bs_sim['lower_bound'] = df_bs_sim[25]
    df_bs_sim['upper_bound'] = df_bs_sim[976]
    df_bs_sim = df_bs_sim.drop(columns=[25, 976])

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.scatter(df_bs_sim['value'], df_bs_sim['actual'], c='black')
    j = -7

    plt.rcParams['font.size'] = '16'

    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(15)
    
    for i in range (0, 13):
        j+=1
        plt.plot([j, j], [df_bs_sim.iloc[i, 2], df_bs_sim.iloc[i, 3]], linewidth=3, color='red')
        plt.gcf().set_size_inches((13, 9))   
        ax.legend(['95% confidence interval'])
        plt.xlabel("Bride’s class minus groom’s class", fontsize=15)
        plt.ylabel("Proportion", fontsize=15)
    plt.show()