import matplotlib as plt
import pandas as pd
from pandas.core.common import flatten
import numpy as np
from statsmodels.formula.api import ols
from statsmodels.iolib.summary2 import summary_col
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS


'''sample'''
def sample_a(d, x, y):

    df = d.copy() 
    
    df[x] = pd.to_numeric(df[x], downcast='integer')
    df[y] = pd.to_numeric(df[y], downcast='integer')
    df['classdiff'] = df[x] - df[y]

    conditions1 = [
    (df[x] <= df[y]) & (df[y].notnull()) & (df[y] != 7), # df[y] != np.nan
    (df[x] > df[y]) & (df[x].notnull()) & (df[y] != 7), # df[y] != np.nan
    (df[y] ==  7)]
    
    choices1 = [0, 1, np.nan]
    df['mardn'] = np.select(conditions1, choices1, np.nan) # np.select(conditions2, choices, None)

    conditions2 = [
    (df[x] <= 7) & (df[x] >= 5),
    (df[x] < 5)]

    choices2 = [1, 0]
    df['lowbr'] = np.select(conditions2, choices2, np.nan) # np.select(conditions2, choices, None)

    df['agebrd'] = df['agebr']/100
    df['agegrd'] = df['agegr']/100
    
    return df


'''Table 2'''
def table_2(df):
    
    df['post_mortality'] = df['post']*df['mortality']
    lst1 = ['singm_19', 'singm_29d', 'singm_39d', 'singm_49d']
    lst2 = ['singf_19', 'singf_29d', 'singf_39d', 'singf_49d']
    lst3 = ['divm_29d', 'divm_39d', 'divm_49d']
    lst4 = ['divf_29d', 'divf_39d', 'divf_49d']
    lst5 = ['widm_29d', 'widm_39d', 'widm_49d']
    lst6 = ['widf_29d', 'widf_39d', 'widf_49d']

    i = 0
    
    for lst in [lst1, lst2, lst3, lst4, lst5, lst6]:
        i += 1
        col = []
        dict = {}
        for var in lst:
            formula = var + "~ post_mortality + post + C(depc)"
            results = ols(formula, data=df).fit()
            table_star = summary_col([results],stars=True).tables[0]
            col.extend((table_star.iloc[-6,].tolist(), table_star.iloc[-5,].tolist()))
            col = list(flatten(col))
            globals()["v" + str(i)] = col
    
    table2 = pd.DataFrame.from_dict({'Single males': v1, 'Single females': v2, 
                                     'Divorced males': v3, 'Divorced females': v4, 
                                     'Widowed males': v5, 'Widowed females': v6}, orient='index').T
    mask = ~(table2.columns.isin(['Single males','Single females']))
    cols_to_shift = table2.columns[mask]
    table2[cols_to_shift] = table2[cols_to_shift].shift(2)
    table2['Age group:'] = ['15–19', '', '20–29', '', '30–39', '', '40–49', '']
    table2 = table2.set_index('Age group:')

    return table2


'''Table 3'''
def table_3(df):
    
    s = (' All', 'classes of', ' groom', 'Excluding ', 'grooms of class ', '1 and 2')
    row_name = ['Dependent variable', 'Percent of soldiers killed x postwar', '', 'Postwar', '', 'Rural', '', 
                'Bride’s age (/100)', '', 'Groom’s Age (/100)', '', 'Groom class dummies', 
                'Département dummies', '$R^{2}$', 'Observations']

    table3_1 = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: [], s[3]: [], s[4]: [], s[5]: []}, orient='index').T
    table3_1[' '] = row_name
    table3_1 = table3_1.set_index(' ')
    table3_1.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride', 
                                          'Class difference', 'Married down', 'Low-class bride']

    for ind in ['classdiff', 'mardn', 'lowbr', 'post_mortality', 'post', 'rural', 'agebrd', 'agegrd', 'clgr', 'depc']:
        df[ind] = pd.to_numeric(df[ind], downcast='float')
    
    lst = ['classdiff', 'mardn', 'lowbr']
    sample = [df, df[df['clgr']>=3]]

    i = 0

    for k in [0, 1]:
        df_a = sample[k]
        for var in lst:
            i += 1
            formula = var + "~ post_mortality + post + rural + agebrd + agegrd + C(clgr) + C(depc)"
            results = smf.ols(formula, data=df_a).fit(cov_type = 'cluster', cov_kwds = {'groups': df_a[[var, 'post_mortality', 
                                                                                        'post', 'rural', 'agebrd', 'agegrd', 'clgr', 'depc']].dropna()['depc']})
            table_star = summary_col([results],stars=True).tables[0]
            
            a = [] 
            a.append(int(results.nobs))
            b = table_star.loc['post_mortality':'R-squared',].to_numpy().tolist() + ['Yes', 'Yes'] + a
            b = list(flatten(b))
            b[10], b[11], b[12] = b[12], b[11], b[10]
            j = i - 1
            table3_1.iloc[1:15, j] = b

    return table3_1


''' Table 4'''
def table_4(df):
    
    s = ('Class', ' defined by', ' father occupation', 'Classes imputed', ' using background ', ' characteristics')
    row_name = ['Dependent variable', 'Percent of soldiers killed x postwar', '', 'Postwar', '', 'Rural', '', 
                'Bride’s age (/100)', '', 'Groom’s Age (/100)', '', 'Groom class dummies', 'Groom half-class dummies', 
                'Département dummies', '$R^{2}$', 'Observations']

    table4_1 = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: [], s[3]: [], s[4]: [], s[5]: []}, orient='index').T
    table4_1[' '] = row_name
    table4_1 = table4_1.set_index(' ')
    table4_1.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride', 
                                          'Class difference', 'Married down', 'Low-class bride']

    for ind in ['classdiff', 'mardn', 'lowbr', 'post_mortality', 'post', 'rural', 'agebrd', 'agegrd', 'clfgr', 'depc']:
        df[ind] = pd.to_numeric(df[ind], downcast='float')
    
    lst = ['classdiff', 'mardn', 'lowbr']
    sample = [df, df]

    i = 0

    for k in [0, 1]:
        df_a = sample[k]
        for var in lst:
            i += 1
            formula = var + "~ post_mortality + post + rural + agebrd + agegrd + C(clfgr) + C(depc)"
            results = smf.ols(formula, data=df_a).fit(cov_type = 'cluster', 
                       cov_kwds = {'groups': df_a[[var, 'post_mortality', 
                                                   'post', 'rural', 'agebrd', 'agegrd', 'clfgr', 
                                                   'depc']].dropna()['depc']})
            table_star = summary_col([results],stars=True).tables[0]
            
            a = [] 
            a.append(int(results.nobs))
            b = table_star.loc['post_mortality':'R-squared',].to_numpy().tolist() + ['Yes', ' ', 'Yes'] + a
            b = list(flatten(b))
            b[10], b[11], b[12], b[13] = b[13], b[12], b[11], b[10]
            j = i - 1
            table4_1.iloc[1:16, j] = b

    return table4_1


'''Table 5'''
def table_5_a(df):
    
    s = (' Class ', 'defined by own', ' occupation ', ' Class  ', 'defined by father', ' occupation  ')
    row_name = ['Dependent variable', 'Panel A. Stage 2 regressions', 'Postwar', '', 
                'Rural', '', 'Bride’s age (/100)', '', 'Groom’s age (/100)', '', 'Sex ratio (men/women)', '', 'Groom class dummies', 'Département dummies',
                '$R^{2}$', 'Observations']

    table_5_a = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: [], s[3]: [], s[4]: [], s[5]: []}, orient='index').T
    table_5_a[' '] = row_name
    table_5_a = table_5_a.set_index(' ')
    table_5_a.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride', 'Class difference', 'Married down', 'Low-class bride']
    lst = ['classdiff', 'mardn', 'lowbr']
    indep = ['clgr', 'clfgr']

    i = 0

    for k in [0, 1]:
        df_a = df[k]
        ind = "C(" + indep[k] + ")"
        for var in lst:
            i += 1
            
            df_a[['sr_predict']] = pd.DataFrame(smf.ols(formula="sr ~ post_mortality", data=df_a).fit(cov_type = 'cluster', 
                                                        cov_kwds = {'groups': df_a[['sr', 'post_mortality', 'depc']].dropna()['depc']}).predict())
            formula = var + '~ post + rural + agebrd + agegrd + ' + ind + ' + C(depc) + sr_predict'
            results = smf.ols(formula, data=df_a).fit(cov_type = 'cluster', cov_kwds = {'groups': df_a[[var, 'sr_predict', 
                                                                                        'post', 'rural', 'agebrd', 'agegrd', indep[k], 'depc']].dropna()['depc']})
            table_star = summary_col([results],stars=True).tables[0]
            
            a = [] 
            a.append(int(results.nobs))
            b = table_star.loc['post':'R-squared',].to_numpy().tolist() + ['Yes', 'Yes'] + a
            b = list(flatten(b))
            b[10], b[12] = b[12], b[10]
            j = i - 1
            table_5_a.iloc[2:16, j] = b

    return table_5_a


'''Table A5'''
def table_a5(df):
    
    s = (' Class ', 'defined by own', ' occupation ', ' Class  ', 'defined by father', ' occupation  ')
    row_name = ['Dependent variable', 'Panel A', 'Percent of soldiers killed x postwar', '', 'Percent of soldiers killed', '', 
                'Postwar', '', 'Rural', '', 'Bride’s age (/100)', '', 'Groom’s Age (/100)', '', 'Groom class dummies',
                'Groom half-class dummies', '$R^{2}$', 'Observations']

    table_a5 = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: [], s[3]: [], s[4]: [], s[5]: []}, orient='index').T
    table_a5[' '] = row_name
    table_a5 = table_a5.set_index(' ')
    table_a5.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride', 'Class difference', 'Married down', 'Low-class bride']    
    lst = ['classdiff', 'mardn', 'lowbr']
    indep = ['clgr', 'clfgr']

    i = 0

    for k in [0, 1]:
        df_a = df[k]
        ind = "C(" + indep[k] + ")"
        for var in lst:
            i += 1
            formula = var + "~ post_mortality + mortality + post + rural + agebrd + agegrd + " + ind
            results = smf.ols(formula, data=df_a).fit(cov_type = 'cluster', cov_kwds = {'groups': df_a[[var, 'post_mortality', 'mortality', 
                                                                                        'post', 'rural', 'agebrd', 'agegrd', indep[k], 'depc']].dropna()['depc']})
            table_star = summary_col([results],stars=True).tables[0]
            
            a = [] 
            a.append(int(results.nobs))
            b = table_star.loc['post_mortality':'R-squared',].to_numpy().tolist() + ['Yes', 'No'] + a
            b = list(flatten(b))
            b[14], b[12], b[13] = b[12], b[13], b[14]
            j = i - 1
            table_a5.iloc[2:18, j] = b

    return table_a5


'''Table A6'''
def table_a6(df):
    
    s = (' Class ', 'defined by own', ' occupation ', ' Class  ', 'defined by father', ' occupation  ')
    row_name = ['Dependent variable', 'Sex ratio (males/females)', '', 'Postwar', '', 'Rural', '', 
                'Bride’s age (/100)', '', 'Groom’s Age (/100)', '', 'Groom class dummies',
                'Groom half-class dummies', 'Département dummies', '$R^{2}$', 'Observations']

    table_a6 = pd.DataFrame.from_dict({s[0]: [], s[1]: [], 
                                     s[2]: [], s[3]: [], 
                                     s[4]: [], s[5]: []}, orient='index').T
    table_a6[' '] = row_name
    table_a6 = table_a6.set_index(' ')
    table_a6.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride', 'Class difference', 'Married down', 'Low-class bride']    
    lst = ['classdiff', 'mardn', 'lowbr']
    indep = ['clgr', 'clfgr']

    i = 0

    for k in [0, 1]:
        df_a = df[k]
        ind = "C(" + indep[k] + ")"
        for var in lst:
            i += 1
            formula = var + "~ sr + post + rural + agebrd + agegrd + " + ind + " + C(depc)"
            results = smf.ols(formula, data=df_a).fit(cov_type = 'cluster', cov_kwds = {'groups': df_a[[var, 'sr', 'post', 'rural', 'agebrd', 
                                                                                        'agegrd', indep[k], 'depc']].dropna()['depc']})
            table_star = summary_col([results],stars=True).tables[0]
            
            a = [] 
            a.append(int(results.nobs))
            b = table_star.loc['sr':'R-squared',].to_numpy().tolist() + ['Yes', 'No', 'Yes'] + a
            b = list(flatten(b))
            b[10], b[11], b[12], b[13] = b[13], b[12], b[11], b[10]
            j = i - 1
            table_a6.iloc[1:16, j] = b

    return table_a6


'''Table 4 (update)'''

def sample_b(d, x, y):

    df = d.copy()
    
    df[x] = pd.to_numeric(df[x], downcast='integer')
    df[y] = pd.to_numeric(df[y], downcast='integer')
    df['classdiff'] = df[x] - df[y]

    conditions1 = [
    (df[x] <= df[y]) & (df[y].notnull()) & (df[y] != 7), # df[y] != np.nan
    (df[x] > df[y]) & (df[x].notnull()) & (df[y] != 7), # df[y] != np.nan
    (df[y] ==  7)]
    
    choices1 = [0, 1, np.nan]
    df['mardn'] = np.select(conditions1, choices1, np.nan) # np.select(conditions2, choices, None)

    conditions2 = [
    (df[x] <= 7) & (df[x] >= 4.2),
    (df[x] < 4.2)]

    choices2 = [1, 0]
    df['lowbr'] = np.select(conditions2, choices2, np.nan) # np.select(conditions2, choices, None)

    df['agebrd'] = df['agebr']/100
    df['agegrd'] = df['agegr']/100
    
    return df


# write a function to convert a list into comma-separated string
def coma(lst):
    return '{} and {}'.format('+ '.join(lst[:-1]), lst[-1])


def sample4_2_b(d):
    sample4_2 = d.copy()
    # select columns using prefix/suffix 
    # sample4_2.filter(regex='^rFclfbr_',axis=1).head()
    # city size dummies
    # Bride's father's class dummies for 7 non-missing categories
    # Bride's mother's class dummies for 7 non-missing categories
    sample4_2['id'] = sample4_2.index + 1
    sample4_2_1 = pd.get_dummies(sample4_2[['city', 'clfbr', 'clmbr']], prefix = ['city', 'clfbr', 'clmbr'], columns=['city', 'clfbr', 'clmbr'], drop_first = False)
    sample4_2_1['id'] = sample4_2_1.index + 1
    sample4_2 = sample4_2.merge(sample4_2_1, left_on='id', right_on='id', how = 'outer')
    sample4_2 = sample4_2.drop(columns = 'city_other')

    # Dummy for bride's father's class is missing because he is dead
    sample4_2.loc[sample4_2['fdbr'] == 'D', 'Fdbr'] = 1
    sample4_2['Fdbr'] = sample4_2['Fdbr'].fillna(0)
    sample4_2['clfbr'] = pd.to_numeric(sample4_2['clfbr'], downcast='integer')
    sample4_2.loc[sample4_2['clfbr'] <=7, 'Fdbr'] = 0

    # Dummy for bride's mother's class is missing because she is dead
    sample4_2.loc[sample4_2['mdbr'] == 'D', 'Mdbr'] = 1
    sample4_2['Mdbr'] = sample4_2['Mdbr'].fillna(0)
    sample4_2['clmbr'] = pd.to_numeric(sample4_2['clmbr'], downcast='integer')
    sample4_2.loc[sample4_2['clmbr'] <=7, 'Mdbr'] = 0

    # Dummy for bride's father has no occupation
    bride_father_noocc = [38,	216,	397,	573,	1601,	1620,	1684,	1823,	2335,	2424,	2505,	2688,	2745,	2754,	2770,	3029,	3088,	3418,	3503,	3613,	3636,	3654,	3687,	3767,	3995,	4045,	4103,	4118,	4180,	4239,	4251,	4361,	4510,	4567,	4593,	4650,	4670,	4743,	4787,	4796,	4803,	4804,	4814,	4846,	4848,	4921,	4991,	5016,	5100,	5142,	5145,	5241,	5270,	5336,	5347,	5371,	5414,	5445,	5672,	5760,	5877,	5886,	5898,	5995,	6023,	6098,	6134]
    sample4_2['Fnooccbr'] = 0
    sample4_2.loc[bride_father_noocc, 'Fnooccbr'] = 1 # gen Fnooccbr = (clfbr==.a)

    # Dummy for bride's mother has no occupation
    bride_mother_noocc = [13,	28,	40,	57,	66,	67,	72,	76,	78,	80,	82,	83,	91,	94,	96,	103,	106,	108,	112,	135,	141,	144,	150,	152,	158,	159,	161,	164,	168,	174,	189,	191,	195,	199,	208,	209,	212,	216,	217,	227,	238,	246,	348,	367,	370,	375,	376,	377,	378,	382,	383,	387,	388,	389,	392,	393,	394,	395,	397,	400,	402,	403,	407,	409,	413,	419,	422,	423,	425,	428,	429,	430,	431,	436,	440,	445,	446,	456,	459,	460,	462,	463,	464,	465,	466,	467,	472,	473,	474,	475,	476,	477,	479,	480,	481,	485,	486,	487,	488,	489,	490,	491,	492,	493,	495,	496,	497,	499,	500,	502,	506,	507,	508,	509,	510,	513,	514,	519,	521,	522,	523,	525,	527,	528,	530,	531,	533,	535,	539,	545,	547,	551,	553,	557,	558,	563,	565,	566,	573,	576,	577,	578,	581,	583,	584,	591,	595,	600,	602,	607,	609,	613,	619,	626,	627,	638,	641,	643,	645,	654,	660,	661,	663,	666,	667,	668,	669,	671,	678,	682,	687,	688,	690,	694,	695,	699,	704,	706,	708,	715,	718,	719,	720,	722,	729,	730,	735,	736,	737,	738,	740,	742,	744,	745,	748,	751,	752,	754,	761,	762,	766,	774,	776,	780,	782,	783,	784,	786,	787,	789,	792,	795,	798,	808,	810,	815,	824,	842,	851,	854,	862,	874,	876,	897,	907,	910,	913,	914,	917,	923,	928,	929,	934,	936,	937,	938,	942,	943,	945,	962,	964,	985,	998,	1004,	1009,	1019,	1023,	1024,	1048,	1058,	1069,	1076,	1077,	1081,	1082,	1094,	1099,	1106,	1107,	1108,	1112,	1114,	1118,	1119,	1123,	1133,	1138,	1181,	1193,	1206,	1209,	1211,	1212,	1219,	1225,	1226,	1233,	1251,	1253,	1257,	1261,	1269,	1284,	1285,	1287,	1289,	1291,	1298,	1299,	1300,	1301,	1304,	1308,	1311,	1321,	1326,	1334,	1335,	1350,	1352,	1374,	1377,	1381,	1385,	1400,	1401,	1404,	1405,	1406,	1407,	1409,	1410,	1411,	1412,	1413,	1415,	1416,	1418,	1419,	1422,	1423,	1426,	1427,	1428,	1431,	1432,	1433,	1434,	1436,	1437,	1482,	1524,	1525,	1529,	1535,	1548,	1550,	1561,	1564,	1565,	1568,	1569,	1572,	1574,	1578,	1580,	1581,	1582,	1584,	1589,	1590,	1592,	1594,	1595,	1596,	1601,	1611,	1612,	1614,	1618,	1623,	1624,	1626,	1628,	1629,	1631,	1633,	1635,	1637,	1638,	1639,	1646,	1647,	1648,	1649,	1650,	1651,	1654,	1656,	1657,	1659,	1660,	1666,	1676,	1686,	1693,	1694,	1696,	1705,	1706,	1711,	1714,	1716,	1718,	1719,	1722,	1731,	1733,	1735,	1746,	1761,	1822,	1823,	1825,	1828,	1844,	1854,	1857,	1865,	1873,	1880,	1901,	1904,	1905,	1934,	1962,	1968,	1969,	1976,	1981,	1989,	2009,	2013,	2017,	2028,	2035,	2042,	2043,	2051,	2113,	2133,	2134,	2135,	2138,	2139,	2145,	2146,	2147,	2150,	2159,	2163,	2165,	2168,	2169,	2170,	2174,	2181,	2192,	2193,	2195,	2203,	2204,	2211,	2215,	2216,	2225,	2236,	2238,	2240,	2243,	2250,	2262,	2272,	2279,	2289,	2294,	2295,	2299,	2300,	2311,	2312,	2321,	2324,	2332,	2335,	2346,	2353,	2356,	2367,	2371,	2386,	2391,	2392,	2439,	2441,	2442,	2452,	2453,	2455,	2459,	2467,	2469,	2471,	2472,	2473,	2474,	2477,	2478,	2484,	2487,	2488,	2500,	2505,	2524,	2525,	2526,	2528,	2550,	2553,	2558,	2562,	2567,	2586,	2588,	2593,	2600,	2620,	2632,	2653,	2655,	2657,	2659,	2684,	2695,	2705,	2706,	2711,	2714,	2715,	2721,	2735,	2742,	2745,	2754,	2757,	2768,	2773,	2774,	2775,	2787,	2789,	2796,	2803,	2809,	2812,	2819,	2820,	2822,	2833,	2834,	2835,	2860,	2872,	2884,	2890,	2901,	2909,	2912,	2928,	2958,	2968,	2974,	2975,	2979,	2986,	2987,	2989,	2995,	3023,	3027,	3029,	3033,	3040,	3056,	3058,	3062,	3065,	3077,	3078,	3079,	3081,	3083,	3086,	3088,	3106,	3119,	3123,	3151,	3155,	3177,	3179,	3180,	3193,	3202,	3208,	3221,	3241,	3249,	3260,	3265,	3282,	3314,	3329,	3377,	3386,	3404,	3410,	3419,	3426,	3429,	3432,	3435,	3442,	3445,	3450,	3461,	3463,	3474,	3476,	3479,	3485,	3493,	3495,	3497,	3506,	3508,	3511,	3512,	3515,	3516,	3522,	3527,	3528,	3529,	3530,	3534,	3535,	3536,	3541,	3545,	3548,	3550,	3556,	3560,	3562,	3580,	3583,	3584,	3589,	3591,	3592,	3600,	3609,	3611,	3612,	3613,	3615,	3616,	3620,	3622,	3625,	3629,	3634,	3636,	3637,	3639,	3658,	3674,	3687,	3689,	3714,	3718,	3719,	3721,	3722,	3724,	3725,	3730,	3735,	3738,	3740,	3746,	3751,	3752,	3753,	3757,	3758,	3764,	3768,	3770,	3772,	3777,	3778,	3779,	3781,	3783,	3786,	3787,	3789,	3792,	3793,	3795,	3799,	3800,	3804,	3807,	3810,	3812,	3815,	3819,	3832,	3845,	3867,	3868,	3870,	3873,	3882,	3898,	3924,	3927,	3934,	3937,	3947,	3970,	3971,	3972,	3973,	3976,	3982,	3983,	3985,	3988,	3995,	4006,	4030,	4036,	4041,	4043,	4055,	4057,	4060,	4063,	4071,	4073,	4078,	4079,	4081,	4082,	4087,	4088,	4096,	4099,	4108,	4109,	4111,	4113,	4114,	4118,	4122,	4124,	4131,	4132,	4138,	4139,	4146,	4151,	4156,	4161,	4167,	4176,	4181,	4183,	4187,	4193,	4194,	4197,	4199,	4201,	4204,	4209,	4214,	4216,	4218,	4230,	4235,	4237,	4243,	4246,	4248,	4250,	4251,	4254,	4257,	4258,	4260,	4265,	4269,	4274,	4276,	4277,	4285,	4286,	4299,	4300,	4301,	4305,	4306,	4309,	4311,	4314,	4316,	4318,	4322,	4325,	4328,	4336,	4337,	4340,	4341,	4342,	4343,	4344,	4345,	4347,	4352,	4357,	4360,	4361,	4363,	4366,	4367,	4368,	4371,	4374,	4382,	4388,	4389,	4401,	4410,	4413,	4416,	4421,	4423,	4424,	4425,	4426,	4428,	4433,	4434,	4435,	4441,	4444,	4448,	4449,	4454,	4458,	4465,	4468,	4469,	4474,	4481,	4484,	4486,	4487,	4489,	4493,	4498,	4507,	4510,	4517,	4536,	4537,	4538,	4539,	4546,	4548,	4552,	4556,	4558,	4562,	4566,	4568,	4572,	4577,	4583,	4603,	4604,	4610,	4615,	4617,	4618,	4627,	4633,	4636,	4641,	4646,	4650,	4653,	4656,	4660,	4664,	4666,	4670,	4671,	4672,	4673,	4675,	4680,	4683,	4684,	4688,	4691,	4692,	4699,	4700,	4703,	4719,	4727,	4732,	4735,	4741,	4745,	4752,	4765,	4767,	4768,	4779,	4783,	4787,	4791,	4794,	4796,	4798,	4799,	4801,	4803,	4805,	4807,	4809,	4814,	4817,	4821,	4824,	4825,	4833,	4834,	4835,	4837,	4840,	4846,	4847,	4848,	4849,	4852,	4862,	4871,	4872,	4881,	4884,	4885,	4887,	4888,	4889,	4890,	4891,	4897,	4901,	4904,	4905,	4906,	4910,	4914,	4915,	4919,	4922,	4933,	4941,	4942,	4943,	4944,	4946,	4948,	4957,	4961,	4962,	4977,	4984,	4991,	4992,	4993,	4995,	5000,	5007,	5016,	5028,	5034,	5036,	5041,	5043,	5044,	5047,	5053,	5065,	5067,	5068,	5071,	5072,	5073,	5080,	5086,	5088,	5091,	5100,	5101,	5103,	5128,	5131,	5132,	5137,	5142,	5145,	5146,	5150,	5151,	5158,	5164,	5166,	5176,	5179,	5180,	5189,	5196,	5197,	5198,	5202,	5203,	5207,	5212,	5222,	5233,	5234,	5245,	5247,	5250,	5255,	5265,	5266,	5270,	5279,	5281,	5282,	5289,	5293,	5298,	5303,	5305,	5306,	5310,	5316,	5317,	5320,	5324,	5327,	5330,	5331,	5333,	5335,	5336,	5339,	5344,	5347,	5348,	5352,	5353,	5355,	5357,	5360,	5362,	5368,	5371,	5372,	5379,	5381,	5383,	5393,	5395,	5398,	5400,	5401,	5402,	5404,	5410,	5414,	5415,	5416,	5422,	5423,	5426,	5427,	5429,	5431,	5432,	5433,	5434,	5436,	5439,	5440,	5441,	5445,	5448,	5457,	5459,	5464,	5474,	5482,	5487,	5504,	5506,	5508,	5510,	5511,	5512,	5513,	5517,	5519,	5522,	5526,	5528,	5531,	5532,	5534,	5535,	5537,	5538,	5539,	5540,	5541,	5546,	5547,	5548,	5549,	5550,	5556,	5559,	5560,	5561,	5562,	5565,	5567,	5569,	5570,	5571,	5573,	5575,	5579,	5582,	5583,	5585,	5586,	5594,	5595,	5596,	5602,	5605,	5607,	5608,	5609,	5612,	5613,	5618,	5621,	5622,	5623,	5625,	5627,	5628,	5629,	5631,	5637,	5638,	5639,	5640,	5643,	5646,	5647,	5649,	5650,	5672,	5673,	5677,	5683,	5684,	5687,	5706,	5712,	5719,	5720,	5722,	5723,	5724,	5725,	5731,	5732,	5733,	5735,	5737,	5738,	5739,	5741,	5742,	5747,	5749,	5750,	5751,	5756,	5761,	5771,	5782,	5790,	5794,	5799,	5808,	5810,	5812,	5817,	5827,	5832,	5833,	5841,	5842,	5845,	5848,	5849,	5853,	5855,	5856,	5858,	5859,	5861,	5862,	5865,	5869,	5874,	5877,	5881,	5883,	5886,	5887,	5891,	5898,	5901,	5902,	5903,	5911,	5921,	5923,	5944,	5952,	5976,	5991,	5997,	6000,	6001,	6002,	6003,	6004,	6007,	6008,	6013,	6015,	6016,	6019,	6020,	6022,	6023,	6024,	6025,	6026,	6027,	6031,	6039,	6041,	6042,	6043,	6044,	6047,	6050,	6051,	6055,	6062,	6072,	6073,	6074,	6082,	6083,	6092,	6094,	6095,	6099,	6102,	6105,	6107,	6108,	6109,	6111,	6116,	6118,	6121,	6127,	6129,	6135,	6139,	6140,	6141,	6143,	6145,	6149,	6155,	6157,	6158,	6161,	6163,	6164,	6166,	6168,	6175,	6179,	6183,	6186,	6189,	6194,	6195]
    sample4_2['Mnooccbr'] = 0
    sample4_2.loc[bride_mother_noocc, 'Mnooccbr'] = 1 # gen Mnooccbr = (clmbr==.a)

    for i in range(1, 8):
        sample4_2['rFclfbr_%i'% i] = sample4_2['rural']*sample4_2['clfbr_%i'% i]
        sample4_2['rMclmbr_%i'% i] = sample4_2['rural']*sample4_2['clmbr_%i'% i]

    varlist = ['Fdbr', 'Mdbr', 'Fnooccbr', 'Mnooccbr']
    for i in varlist:
        sample4_2['r'+i] = sample4_2['rural']*sample4_2[i]
    
    #############################################################

    # Groom's father's class dummies for 7 non-missing categories
    # Groom's mother's class dummies for 7 non-missing categories
    sample4_2_2 = pd.get_dummies(sample4_2[['clfgr', 'clmgr']], prefix = ['clfgr', 'clmgr'], columns=['clfgr', 'clmgr'], drop_first = False)
    sample4_2_2['id'] = sample4_2_2.index + 1
    sample4_2 = sample4_2.merge(sample4_2_2, left_on='id', right_on='id', how = 'outer')

    # Dummy for groom's father's class is missing because he is dead
    sample4_2.loc[sample4_2['fdgr'] == 'D', 'Fdgr'] = 1
    sample4_2['Fdgr'] = sample4_2['Fdgr'].fillna(0)
    sample4_2['clfgr'] = pd.to_numeric(sample4_2['clfgr'], downcast='integer')
    sample4_2.loc[sample4_2['clfgr'] <=7, 'Fdgr'] = 0

    # Dummy for groom's mother's class is missing because she is dead
    sample4_2.loc[sample4_2['mdgr'] == 'D', 'Mdgr'] = 1
    sample4_2['Mdgr'] = sample4_2['Mdgr'].fillna(0)
    sample4_2['clmgr'] = pd.to_numeric(sample4_2['clmgr'], downcast='integer')
    sample4_2.loc[sample4_2['clmgr'] <=7, 'Mdgr'] = 0

    # Dummy for groom's father has no occupation
    bride_father_noocc1 = [584,	672,	729,	798,	824,	829,	859,	1058,	1093,	1106,	1138,	1211,	1310,	1572,	1635,	2230,	2376,	2380,	2506,	2528,	2689,	2754,	2788,	2798,	2898,	2940,	2955,	3000,	3417,	3427,	3518,	3561,	3567,	3577,	3613,	3812,	3861,	4009,	4032,	4045,	4057,	4084,	4099,	4127,	4194,	4274,	4275,	4320,	4332,	4337,	4340,	4361,	4417,	4435,	4440,	4568,	4571,	4636,	4692,	4724,	4758,	4800,	4838,	4981,	5036,	5065,	5197,	5233,	5245,	5283,	5317,	5320,	5347,	5374,	5485,	5494,	5679,	5790,	5946,	5951,	6009,	6026,	6094,	6129,	6171]
    sample4_2['Fnooccgr'] = 0
    sample4_2.loc[bride_father_noocc1, 'Fnooccgr'] = 1 

    # Dummy for groom's mother has no occupation
    bride_mother_noocc1 = [14,	28,	55,	57,	61,	62,	63,	65,	66,	70,	76,	77,	80,	82,	83,	90,	96,	103,	104,	105,	106,	109,	131,	141,	145,	150,	153,	156,	157,	164,	165,	168,	170,	174,	183,	186,	188,	198,	209,	210,	212,	216,	238,	246,	348,	349,	366,	368,	375,	376,	382,	383,	388,	389,	392,	393,	394,	400,	404,	407,	408,	412,	419,	422,	423,	425,	430,	431,	438,	440,	441,	445,	456,	459,	464,	465,	466,	469,	471,	472,	473,	474,	475,	476,	477,	480,	481,	485,	486,	489,	493,	494,	495,	497,	499,	501,	503,	504,	506,	509,	511,	513,	518,	519,	520,	521,	522,	524,	526,	528,	529,	530,	532,	533,	534,	536,	539,	546,	549,	551,	554,	557,	558,	563,	565,	566,	577,	583,	584,	586,	591,	593,	598,	600,	603,	605,	607,	609,	619,	627,	630,	632,	634,	635,	643,	644,	648,	649,	651,	658,	660,	661,	666,	669,	670,	671,	676,	678,	683,	687,	694,	696,	697,	699,	702,	703,	704,	706,	708,	715,	718,	722,	737,	738,	740,	742,	744,	746,	748,	749,	752,	754,	755,	761,	762,	766,	767,	768,	769,	774,	776,	777,	779,	782,	783,	784,	786,	788,	789,	792,	795,	796,	797,	798,	803,	808,	830,	842,	845,	850,	851,	854,	862,	871,	876,	877,	881,	897,	902,	911,	913,	914,	918,	923,	928,	929,	934,	936,	937,	938,	939,	943,	945,	960,	964,	970,	985,	998,	1004,	1006,	1007,	1009,	1054,	1066,	1077,	1081,	1082,	1091,	1096,	1106,	1108,	1130,	1138,	1145,	1146,	1165,	1171,	1175,	1183,	1193,	1211,	1219,	1221,	1229,	1243,	1248,	1251,	1256,	1259,	1263,	1272,	1276,	1281,	1287,	1290,	1298,	1300,	1301,	1304,	1316,	1322,	1326,	1334,	1335,	1350,	1360,	1367,	1377,	1378,	1385,	1392,	1395,	1399,	1401,	1405,	1411,	1412,	1414,	1415,	1416,	1418,	1420,	1421,	1422,	1423,	1427,	1428,	1431,	1433,	1434,	1522,	1529,	1531,	1536,	1548,	1552,	1556,	1558,	1561,	1564,	1567,	1569,	1576,	1578,	1580,	1581,	1584,	1586,	1590,	1591,	1595,	1596,	1598,	1601,	1604,	1606,	1614,	1616,	1618,	1623,	1624,	1626,	1628,	1629,	1633,	1634,	1636,	1638,	1639,	1640,	1642,	1644,	1648,	1649,	1654,	1657,	1658,	1659,	1661,	1676,	1677,	1702,	1706,	1709,	1711,	1712,	1714,	1718,	1719,	1722,	1732,	1733,	1746,	1752,	1761,	1796,	1800,	1814,	1820,	1822,	1823,	1825,	1828,	1831,	1837,	1844,	1854,	1857,	1867,	1873,	1901,	1902,	1909,	1919,	1945,	1962,	1964,	1966,	1981,	1987,	2013,	2017,	2032,	2035,	2043,	2080,	2081,	2085,	2111,	2133,	2134,	2136,	2144,	2146,	2150,	2152,	2153,	2159,	2163,	2165,	2167,	2178,	2189,	2193,	2195,	2197,	2205,	2207,	2215,	2216,	2217,	2230,	2234,	2238,	2240,	2243,	2245,	2250,	2252,	2272,	2284,	2295,	2299,	2310,	2312,	2332,	2335,	2338,	2340,	2342,	2345,	2346,	2347,	2351,	2352,	2353,	2365,	2371,	2376,	2382,	2419,	2428,	2453,	2468,	2469,	2471,	2473,	2474,	2477,	2478,	2479,	2480,	2484,	2488,	2499,	2505,	2518,	2519,	2526,	2528,	2537,	2539,	2543,	2545,	2548,	2551,	2552,	2559,	2567,	2581,	2582,	2586,	2620,	2632,	2642,	2643,	2655,	2657,	2659,	2667,	2684,	2688,	2695,	2705,	2706,	2711,	2714,	2719,	2721,	2730,	2732,	2735,	2742,	2745,	2754,	2768,	2774,	2775,	2777,	2788,	2790,	2798,	2808,	2820,	2822,	2826,	2839,	2866,	2869,	2872,	2884,	2889,	2891,	2898,	2911,	2915,	2928,	2957,	2958,	2962,	2966,	2976,	2979,	2986,	2987,	2989,	2993,	2995,	2996,	3013,	3016,	3023,	3033,	3035,	3048,	3049,	3056,	3058,	3062,	3077,	3078,	3081,	3111,	3114,	3117,	3123,	3151,	3179,	3180,	3185,	3187,	3193,	3195,	3202,	3220,	3248,	3249,	3260,	3265,	3274,	3314,	3322,	3333,	3341,	3364,	3377,	3386,	3399,	3406,	3409,	3410,	3415,	3417,	3422,	3426,	3427,	3430,	3431,	3432,	3445,	3450,	3457,	3469,	3479,	3506,	3513,	3515,	3516,	3520,	3522,	3527,	3528,	3529,	3530,	3535,	3536,	3541,	3545,	3548,	3549,	3550,	3554,	3556,	3563,	3566,	3567,	3579,	3580,	3582,	3583,	3584,	3600,	3609,	3611,	3613,	3616,	3617,	3620,	3625,	3632,	3633,	3634,	3638,	3639,	3641,	3652,	3658,	3671,	3674,	3679,	3687,	3693,	3704,	3707,	3711,	3714,	3718,	3719,	3721,	3722,	3724,	3725,	3730,	3731,	3735,	3740,	3744,	3746,	3751,	3752,	3753,	3757,	3758,	3766,	3768,	3772,	3777,	3778,	3779,	3781,	3782,	3783,	3785,	3786,	3787,	3789,	3791,	3792,	3793,	3799,	3800,	3804,	3808,	3810,	3817,	3819,	3836,	3845,	3860,	3861,	3867,	3872,	3873,	3898,	3924,	3927,	3934,	3980,	3986,	3995,	4001,	4004,	4006,	4015,	4021,	4022,	4030,	4032,	4034,	4037,	4039,	4041,	4044,	4045,	4058,	4063,	4064,	4065,	4067,	4071,	4073,	4078,	4079,	4082,	4099,	4103,	4104,	4107,	4108,	4109,	4114,	4117,	4127,	4131,	4132,	4133,	4136,	4144,	4145,	4150,	4151,	4152,	4156,	4158,	4161,	4163,	4166,	4171,	4172,	4173,	4182,	4183,	4185,	4187,	4191,	4192,	4199,	4204,	4209,	4211,	4212,	4213,	4218,	4220,	4223,	4230,	4232,	4234,	4235,	4236,	4237,	4239,	4243,	4247,	4248,	4250,	4260,	4268,	4274,	4275,	4284,	4285,	4286,	4296,	4300,	4302,	4306,	4308,	4311,	4314,	4318,	4320,	4323,	4327,	4328,	4335,	4336,	4337,	4341,	4344,	4345,	4352,	4356,	4357,	4360,	4366,	4367,	4368,	4370,	4371,	4374,	4377,	4378,	4389,	4395,	4397,	4401,	4410,	4426,	4428,	4433,	4435,	4440,	4441,	4444,	4450,	4454,	4458,	4460,	4464,	4473,	4475,	4481,	4487,	4488,	4491,	4492,	4493,	4496,	4500,	4504,	4510,	4517,	4524,	4532,	4533,	4534,	4537,	4539,	4545,	4549,	4552,	4556,	4559,	4562,	4566,	4568,	4571,	4572,	4577,	4583,	4590,	4617,	4618,	4624,	4627,	4629,	4633,	4641,	4650,	4652,	4653,	4662,	4663,	4664,	4666,	4669,	4671,	4673,	4674,	4675,	4680,	4682,	4683,	4684,	4688,	4697,	4700,	4703,	4716,	4719,	4720,	4722,	4724,	4727,	4728,	4732,	4737,	4739,	4744,	4753,	4754,	4757,	4759,	4763,	4765,	4768,	4770,	4780,	4781,	4797,	4798,	4799,	4800,	4801,	4805,	4806,	4807,	4813,	4814,	4816,	4817,	4834,	4835,	4837,	4838,	4839,	4840,	4852,	4853,	4857,	4862,	4863,	4872,	4884,	4885,	4888,	4889,	4891,	4892,	4893,	4897,	4898,	4901,	4904,	4906,	4910,	4914,	4915,	4918,	4919,	4920,	4922,	4925,	4933,	4934,	4936,	4944,	4945,	4948,	4954,	4956,	4962,	4963,	4964,	4965,	4970,	4973,	4977,	4978,	4983,	4984,	4991,	4992,	4994,	5000,	5009,	5010,	5011,	5012,	5015,	5016,	5017,	5019,	5020,	5021,	5022,	5028,	5030,	5036,	5043,	5044,	5045,	5046,	5047,	5058,	5067,	5071,	5074,	5091,	5094,	5095,	5096,	5098,	5100,	5119,	5123,	5125,	5128,	5141,	5146,	5150,	5154,	5158,	5162,	5164,	5165,	5166,	5170,	5171,	5175,	5176,	5177,	5181,	5184,	5185,	5188,	5189,	5194,	5197,	5200,	5201,	5202,	5203,	5207,	5211,	5212,	5224,	5232,	5245,	5246,	5250,	5253,	5255,	5256,	5257,	5258,	5261,	5268,	5270,	5279,	5281,	5282,	5283,	5287,	5290,	5293,	5296,	5298,	5310,	5315,	5317,	5330,	5332,	5335,	5338,	5340,	5344,	5346,	5348,	5352,	5354,	5359,	5360,	5361,	5368,	5371,	5372,	5377,	5383,	5386,	5387,	5388,	5393,	5395,	5396,	5398,	5399,	5401,	5402,	5403,	5404,	5407,	5408,	5412,	5416,	5420,	5421,	5422,	5423,	5424,	5426,	5429,	5430,	5432,	5433,	5434,	5436,	5439,	5440,	5445,	5447,	5448,	5451,	5457,	5464,	5470,	5474,	5475,	5482,	5484,	5486,	5491,	5495,	5497,	5501,	5504,	5508,	5511,	5513,	5516,	5517,	5519,	5520,	5522,	5524,	5528,	5531,	5532,	5534,	5538,	5543,	5545,	5546,	5547,	5548,	5549,	5550,	5556,	5559,	5561,	5562,	5563,	5567,	5569,	5571,	5572,	5582,	5583,	5585,	5586,	5592,	5597,	5602,	5603,	5605,	5608,	5612,	5616,	5618,	5622,	5625,	5628,	5629,	5630,	5631,	5635,	5636,	5641,	5643,	5649,	5650,	5652,	5659,	5669,	5672,	5673,	5679,	5684,	5719,	5720,	5721,	5722,	5723,	5725,	5727,	5730,	5731,	5732,	5733,	5734,	5735,	5737,	5738,	5739,	5743,	5744,	5745,	5747,	5749,	5752,	5754,	5755,	5757,	5760,	5764,	5765,	5773,	5774,	5775,	5780,	5782,	5787,	5790,	5804,	5810,	5813,	5830,	5842,	5844,	5845,	5846,	5848,	5850,	5853,	5855,	5856,	5861,	5862,	5865,	5869,	5873,	5874,	5875,	5877,	5879,	5886,	5887,	5889,	5896,	5897,	5901,	5902,	5906,	5923,	5944,	5947,	5960,	5976,	5978,	5984,	5994,	5999,	6001,	6002,	6003,	6010,	6015,	6016,	6018,	6019,	6020,	6022,	6023,	6024,	6025,	6026,	6029,	6031,	6033,	6035,	6040,	6041,	6044,	6047,	6051,	6052,	6056,	6060,	6062,	6072,	6073,	6076,	6079,	6082,	6083,	6085,	6089,	6094,	6095,	6097,	6099,	6101,	6103,	6104,	6105,	6107,	6108,	6110,	6113,	6114,	6116,	6118,	6123,	6128,	6129,	6140,	6143,	6145,	6146,	6148,	6149,	6151,	6152,	6157,	6159,	6162,	6163,	6164,	6167,	6168,	6169,	6171,	6174,	6177,	6180,	6183,	6185,	6189,	6191,	6194,	6195]
    sample4_2['Mnooccgr'] = 0
    sample4_2.loc[bride_mother_noocc1, 'Mnooccgr'] = 1 

    for i in range(1, 8):
        sample4_2['rGclfgr_%i'% i] = sample4_2['rural']*sample4_2['clfgr_%i'% i]
        sample4_2['rNclmgr_%i'% i] = sample4_2['rural']*sample4_2['clmgr_%i'% i]

    varlist = ['Fdgr', 'Mdgr', 'Fnooccgr', 'Mnooccgr']
    for i in varlist:
        sample4_2['r'+i] = sample4_2['rural']*sample4_2[i]

    sample4_2 = sample4_2.rename(columns={"city_large city": "city_large_city", "city_medium-sized city": "city_medium_sized_city"})
    group_city = sample4_2.filter(regex='city_').columns.tolist()    
    # imputing bride's class (Table A4, first two columns)
    group_clfbr = sample4_2.filter(regex='clfbr_').columns.tolist() # Find column whose name contains a specific string
    group_clmbr = sample4_2.filter(regex='clmbr_').columns.tolist()
    group_rFclfbr = sample4_2.filter(regex='rFclfbr_').columns.tolist()
    group_rMclmbr = sample4_2.filter(regex='rMclmbr_').columns.tolist()

    # imputing groom's class (Table A4, last two columns)
    group_clfgr = sample4_2.filter(regex='clfgr_').columns.tolist() # Find column whose name contains a specific string
    group_clmgr = sample4_2.filter(regex='clmgr_').columns.tolist()
    group_rGclfgr = sample4_2.filter(regex='rGclfgr_').columns.tolist()
    group_rNclmgr = sample4_2.filter(regex='rNclmgr_').columns.tolist()

    # imputing bride's class (Table A4, first two columns)
    formula_1 = 'clbr ~ Fdbr + Mdbr + Fnooccbr + Mnooccbr + rural + rFdbr + rMdbr + rFnooccbr + rMnooccbr + ' + (coma(group_city)).replace('and', '+') + ' + ' + (coma(group_clfbr)).replace('and', '+') + ' + ' + (coma(group_rFclfbr)).replace('and', '+') + ' + ' + (coma(group_clmbr)).replace('and', '+') + ' + ' + (coma(group_rMclmbr)).replace('and', '+')
    # (coma(group_city)).replace('and', '+'): converting a list into comma-separated string
    results_1 = ols(formula_1, data=sample4_2[sample4_2['post']==0]).fit()

    exp_var_1 = []
    for key, value in results_1.params.iteritems(): 
        exp_var_1.append(key)

    sample4_2['Intercept'] = 1 # create variable 'Intercept' for linear combination of OLS regressors
    sample4_2['est_clbr'] = sample4_2[exp_var_1].dot(results_1.params)

    # imputing groom's class (Table A4, last two columns)
    formula_2 = 'clgr ~ Fdgr + Mdgr + Fnooccgr + Mnooccgr + rural + rFdgr + rMdgr + rFnooccgr + rMnooccgr + ' + (coma(group_city)).replace('and', '+') + ' + ' + (coma(group_clfgr)).replace('and', '+') + ' + ' + (coma(group_rGclfgr)).replace('and', '+') + ' + ' + (coma(group_clmgr)).replace('and', '+') + ' + ' + (coma(group_rNclmgr)).replace('and', '+')
    # (coma(group_city)).replace('and', '+'): converting a list into comma-separated string
    results_2 = ols(formula_2, data=sample4_2[sample4_2['post']==0]).fit()

    exp_var_2 = []
    for key, value in results_2.params.iteritems(): 
        exp_var_2.append(key)

    sample4_2['est_clgr'] = sample4_2[exp_var_2].dot(results_2.params)

    # generating groom half-class dummies
    sample4_2['est_clgr_half'] = round(2*sample4_2['est_clgr'])/2

    sample4_2 = sample_b(sample4_2, 'est_clbr', 'est_clgr')

    return sample4_2


''' Update table 4'''


def table_4_t(df, df1):
    
    s = ('Class', ' defined by', ' father occupation', 'Classes imputed', ' using background ', ' characteristics')
    row_name = ['Dependent variable', 'Percent of soldiers killed x postwar', '', 'Postwar', '', 'Rural', '', 
                'Bride’s age (/100)', '', 'Groom’s Age (/100)', '', 'Groom class dummies', 'Groom half-class dummies', 
                'Département dummies', '$R^{2}$', 'Observations']

    table4_1 = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: [], s[3]: [], s[4]: [], s[5]: []}, orient='index').T
    table4_1[' '] = row_name
    table4_1 = table4_1.set_index(' ')
    table4_1.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride', 
                                          'Class difference', 'Married down', 'Low-class bride']

    for ind in ['classdiff', 'mardn', 'lowbr', 'post_mortality', 'post', 'rural', 'agebrd', 'agegrd', 'clfgr', 'depc']:
        df[ind] = pd.to_numeric(df[ind], downcast='float')
    
    lst = ['classdiff', 'mardn', 'lowbr']
    v = ['clfgr', 'est_clgr_half']
    sample = [df, df1]

    i = 0

    for k in [0, 1]:
        df_a = sample[k]
        x = v[k]
        for var in lst:
            i += 1
            formula = var + "~ post_mortality + post + rural + agebrd + agegrd + C(" + x + ") + " + "C(depc)"
            results = smf.ols(formula, data=df_a).fit(cov_type = 'cluster', 
                       cov_kwds = {'groups': df_a[[var, 'post_mortality', 
                                                   'post', 'rural', 'agebrd', 'agegrd', x, 
                                                   'depc']].dropna()['depc']})
            table_star = summary_col([results],stars=True).tables[0]
            
            a = [] 
            a.append(int(results.nobs))
            b = table_star.loc['post_mortality':'R-squared',].to_numpy().tolist() + ['Yes', ' ', 'Yes'] + a
            b = list(flatten(b))
            b[10], b[11], b[12], b[13] = b[13], b[12], b[11], b[10]
            if k == 1:
                b[11], b[10] = b[10], b[11]
            j = i - 1
            table4_1.iloc[1:16, j] = b

    return table4_1


'''Table 6'''

def table_6(d):
    
    df = d.copy()
    #remove 4 rows + 2 string rows, 12 rows
    s = ('(1)', '(2)', '(3)')
    row_name = ['Dependent variable', 'Percent of soldiers killed x postwar', '', 'Postwar', '', 'Rural', '', 
                'Groom class dummies', 'Bride class dummies', 'Département dummies', '$R^{2}$', 'Observations']

    table6_1 = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: []}, orient='index').T
    table6_1[' '] = row_name
    table6_1 = table6_1.set_index(' ')
    table6_1.loc['Dependent variable'] = ['Age difference', 'Groom’s age', 'Bride’s age']

    for ind in ['post', 'rural', 'agegr', 'agebr', 'clbr', 'clgr', 'depc']:
        df[ind] = pd.to_numeric(df[ind], downcast='float')
    
    clbr8 = [0,	1,	10,	17,	20,	26,	31,	34,	36,	39,	40,	41,	42,	43,	51,	53,	55,	61,	65,	67,	70,	71,	72,	74,	76,	78,	80,	81,	82,	84,	87,	90,	91,	96,	97,	103,	104,	105,	106,	108,	111,	115,	133,	135,	141,	144,	146,	147,	148,	153,	156,	157,	158,	160,	164,	169,	170,	171,	172,	174,	183,	184,	186,	188,	189,	190,	191,	194,	199,	204,	210,	216,	219,	221,	225,	227,	229,	245,	249,	259,	271,	272,	276,	278,	284,	285,	291,	298,	306,	312,	327,	330,	337,	338,	340,	348,	349,	366,	369,	370,	371,	375,	376,	378,	379,	381,	382,	383,	385,	387,	388,	389,	390,	392,	393,	394,	396,	397,	400,	401,	402,	404,	407,	408,	410,	412,	413,	414,	418,	421,	422,	425,	428,	430,	431,	432,	436,	437,	438,	440,	441,	443,	444,	445,	446,	451,	452,	453,	454,	455,	456,	457,	458,	459,	460,	461,	462,	463,	464,	467,	469,	470,	471,	473,	474,	475,	476,	478,	479,	480,	481,	482,	483,	484,	485,	486,	487,	488,	489,	490,	492,	494,	495,	497,	498,	500,	501,	504,	506,	507,	508,	510,	513,	514,	515,	517,	518,	522,	524,	525,	526,	527,	528,	530,	533,	534,	535,	536,	541,	545,	547,	549,	551,	552,	553,	559,	560,	564,	570,	573,	578,	581,	587,	589,	591,	592,	593,	597,	600,	602,	604,	607,	608,	609,	610,	611,	613,	614,	617,	618,	622,	623,	626,	628,	629,	630,	633,	637,	638,	644,	645,	651,	652,	661,	663,	664,	674,	677,	680,	682,	683,	687,	688,	690,	692,	695,	696,	701,	704,	706,	708,	711,	715,	718,	719,	720,	722,	724,	725,	726,	728,	729,	730,	732,	733,	736,	737,	738,	739,	740,	741,	742,	744,	745,	746,	748,	749,	751,	752,	754,	755,	762,	766,	768,	770,	774,	776,	777,	779,	780,	782,	783,	784,	786,	787,	790,	793,	794,	795,	796,	797,	798,	801,	803,	806,	807,	808,	811,	814,	823,	824,	830,	833,	834,	841,	847,	852,	854,	857,	858,	861,	862,	863,	868,	869,	871,	872,	874,	875,	876,	877,	881,	883,	886,	892,	897,	898,	902,	904,	907,	908,	910,	911,	912,	913,	914,	915,	918,	921,	922,	923,	924,	925,	927,	928,	929,	931,	932,	934,	935,	936,	937,	938,	939,	940,	941,	942,	943,	944,	945,	946,	950,	956,	960,	962,	970,	971,	980,	985,	989,	991,	998,	1001,	1002,	1007,	1008,	1009,	1012,	1015,	1016,	1018,	1019,	1024,	1025,	1026,	1030,	1035,	1036,	1040,	1044,	1047,	1048,	1049,	1051,	1052,	1058,	1059,	1061,	1062,	1063,	1070,	1074,	1077,	1081,	1084,	1086,	1087,	1089,	1091,	1095,	1096,	1099,	1105,	1108,	1110,	1111,	1112,	1113,	1114,	1116,	1117,	1119,	1120,	1121,	1130,	1134,	1136,	1138,	1146,	1147,	1149,	1151,	1152,	1153,	1155,	1157,	1158,	1159,	1160,	1161,	1162,	1163,	1164,	1165,	1167,	1169,	1170,	1173,	1175,	1176,	1177,	1178,	1179,	1180,	1181,	1183,	1185,	1186,	1187,	1190,	1191,	1192,	1193,	1194,	1198,	1199,	1200,	1201,	1202,	1203,	1204,	1205,	1206,	1208,	1209,	1210,	1211,	1212,	1213,	1214,	1215,	1218,	1219,	1220,	1222,	1223,	1225,	1227,	1228,	1229,	1233,	1235,	1236,	1238,	1239,	1241,	1242,	1243,	1244,	1246,	1248,	1250,	1251,	1252,	1253,	1254,	1257,	1261,	1262,	1263,	1264,	1265,	1267,	1268,	1269,	1270,	1271,	1272,	1273,	1274,	1283,	1285,	1287,	1288,	1289,	1290,	1291,	1293,	1300,	1301,	1306,	1307,	1308,	1315,	1316,	1322,	1323,	1328,	1334,	1335,	1336,	1337,	1350,	1352,	1356,	1358,	1360,	1362,	1367,	1369,	1373,	1377,	1379,	1381,	1383,	1392,	1394,	1395,	1400,	1401,	1402,	1404,	1405,	1406,	1407,	1409,	1410,	1411,	1413,	1414,	1415,	1416,	1418,	1420,	1421,	1422,	1423,	1424,	1425,	1426,	1427,	1428,	1429,	1430,	1431,	1433,	1434,	1435,	1436,	1437,	1482,	1522,	1526,	1528,	1529,	1531,	1535,	1536,	1538,	1542,	1544,	1546,	1548,	1550,	1552,	1553,	1556,	1558,	1560,	1561,	1564,	1567,	1568,	1569,	1570,	1571,	1572,	1574,	1578,	1579,	1581,	1582,	1584,	1586,	1589,	1591,	1592,	1595,	1596,	1598,	1599,	1601,	1602,	1606,	1610,	1613,	1614,	1618,	1620,	1624,	1626,	1628,	1631,	1632,	1633,	1634,	1635,	1636,	1637,	1638,	1639,	1641,	1642,	1646,	1647,	1648,	1650,	1651,	1654,	1655,	1656,	1657,	1659,	1660,	1661,	1662,	1663,	1664,	1666,	1677,	1684,	1686,	1690,	1692,	1695,	1704,	1705,	1708,	1711,	1714,	1719,	1720,	1722,	1725,	1726,	1727,	1728,	1731,	1732,	1733,	1734,	1735,	1739,	1743,	1746,	1747,	1749,	1750,	1751,	1753,	1754,	1756,	1760,	1761,	1771,	1774,	1775,	1800,	1806,	1808,	1814,	1815,	1818,	1821,	1824,	1825,	1827,	1830,	1832,	1836,	1837,	1838,	1842,	1846,	1848,	1849,	1850,	1851,	1852,	1853,	1857,	1859,	1860,	1862,	1865,	1867,	1869,	1873,	1874,	1875,	1879,	1880,	1881,	1882,	1883,	1884,	1890,	1891,	1892,	1895,	1896,	1897,	1901,	1905,	1907,	1909,	1917,	1918,	1925,	1927,	1928,	1934,	1944,	1946,	1947,	1948,	1960,	1962,	1965,	1968,	1974,	1975,	1976,	1981,	1989,	1997,	2013,	2017,	2020,	2035,	2036,	2037,	2040,	2044,	2050,	2053,	2066,	2077,	2085,	2090,	2098,	2107,	2113,	2116,	2133,	2134,	2135,	2136,	2137,	2142,	2143,	2145,	2146,	2147,	2148,	2152,	2155,	2156,	2160,	2163,	2164,	2165,	2167,	2168,	2169,	2170,	2172,	2174,	2176,	2178,	2180,	2181,	2182,	2184,	2193,	2195,	2199,	2202,	2203,	2205,	2206,	2208,	2215,	2216,	2217,	2218,	2236,	2243,	2250,	2261,	2279,	2281,	2287,	2288,	2289,	2290,	2292,	2293,	2294,	2307,	2310,	2313,	2319,	2321,	2324,	2325,	2326,	2327,	2330,	2335,	2338,	2339,	2340,	2342,	2346,	2351,	2352,	2353,	2358,	2371,	2379,	2382,	2392,	2414,	2429,	2431,	2432,	2434,	2435,	2436,	2437,	2438,	2439,	2440,	2441,	2442,	2445,	2446,	2448,	2451,	2455,	2459,	2461,	2464,	2466,	2468,	2469,	2472,	2473,	2474,	2476,	2477,	2482,	2483,	2484,	2487,	2489,	2491,	2492,	2497,	2499,	2500,	2502,	2503,	2513,	2514,	2517,	2519,	2525,	2527,	2533,	2542,	2543,	2547,	2550,	2551,	2553,	2558,	2559,	2560,	2561,	2562,	2568,	2576,	2577,	2581,	2582,	2592,	2596,	2598,	2600,	2601,	2604,	2611,	2625,	2627,	2629,	2636,	2638,	2639,	2642,	2643,	2646,	2650,	2651,	2652,	2653,	2655,	2660,	2663,	2667,	2671,	2673,	2678,	2681,	2683,	2686,	2688,	2690,	2693,	2695,	2700,	2705,	2707,	2710,	2711,	2712,	2714,	2715,	2718,	2720,	2724,	2726,	2730,	2732,	2737,	2747,	2748,	2754,	2757,	2762,	2767,	2768,	2774,	2778,	2784,	2789,	2790,	2792,	2794,	2795,	2802,	2804,	2807,	2809,	2812,	2821,	2824,	2826,	2827,	2830,	2831,	2833,	2834,	2835,	2836,	2838,	2840,	2841,	2846,	2847,	2851,	2852,	2853,	2855,	2856,	2860,	2861,	2862,	2864,	2865,	2866,	2869,	2872,	2873,	2876,	2877,	2879,	2880,	2881,	2885,	2887,	2889,	2890,	2891,	2893,	2897,	2898,	2901,	2909,	2910,	2911,	2912,	2918,	2921,	2922,	2924,	2931,	2932,	2933,	2934,	2936,	2938,	2939,	2942,	2943,	2948,	2949,	2951,	2953,	2954,	2957,	2960,	2962,	2963,	2964,	2965,	2968,	2971,	2972,	2973,	2975,	2976,	2979,	2987,	2990,	2993,	2994,	2995,	2996,	2997,	3002,	3004,	3006,	3009,	3010,	3011,	3013,	3016,	3018,	3019,	3022,	3023,	3025,	3026,	3029,	3031,	3035,	3036,	3037,	3039,	3040,	3043,	3044,	3047,	3049,	3052,	3056,	3057,	3059,	3060,	3061,	3062,	3063,	3064,	3065,	3068,	3069,	3074,	3078,	3081,	3082,	3083,	3084,	3085,	3086,	3100,	3101,	3103,	3107,	3111,	3114,	3118,	3119,	3123,	3125,	3133,	3135,	3136,	3139,	3140,	3143,	3151,	3152,	3155,	3156,	3160,	3164,	3166,	3167,	3169,	3172,	3177,	3178,	3179,	3180,	3181,	3182,	3183,	3185,	3186,	3187,	3188,	3189,	3190,	3191,	3192,	3195,	3201,	3202,	3203,	3204,	3206,	3207,	3211,	3214,	3219,	3220,	3221,	3223,	3225,	3226,	3229,	3230,	3235,	3237,	3240,	3241,	3242,	3247,	3249,	3250,	3252,	3253,	3254,	3256,	3261,	3264,	3265,	3267,	3270,	3273,	3274,	3275,	3276,	3277,	3280,	3281,	3282,	3283,	3284,	3285,	3286,	3287,	3289,	3292,	3294,	3298,	3301,	3302,	3303,	3304,	3307,	3309,	3310,	3312,	3314,	3317,	3318,	3319,	3323,	3325,	3327,	3328,	3329,	3331,	3333,	3334,	3335,	3336,	3339,	3341,	3342,	3344,	3345,	3351,	3357,	3358,	3359,	3361,	3362,	3364,	3365,	3366,	3370,	3372,	3373,	3374,	3376,	3377,	3380,	3383,	3387,	3388,	3390,	3391,	3396,	3404,	3423,	3432,	3442,	3445,	3446,	3450,	3451,	3452,	3464,	3466,	3469,	3472,	3474,	3475,	3479,	3482,	3485,	3486,	3495,	3506,	3511,	3515,	3516,	3519,	3522,	3526,	3527,	3528,	3529,	3534,	3535,	3536,	3540,	3542,	3545,	3547,	3549,	3552,	3562,	3563,	3578,	3580,	3582,	3583,	3589,	3590,	3592,	3600,	3610,	3611,	3612,	3613,	3614,	3615,	3618,	3621,	3626,	3627,	3629,	3630,	3632,	3633,	3634,	3639,	3653,	3654,	3656,	3658,	3663,	3665,	3666,	3671,	3672,	3681,	3682,	3685,	3689,	3691,	3692,	3695,	3704,	3706,	3707,	3708,	3714,	3718,	3719,	3720,	3721,	3724,	3725,	3726,	3729,	3730,	3731,	3735,	3738,	3740,	3745,	3746,	3749,	3751,	3752,	3753,	3764,	3767,	3768,	3770,	3772,	3777,	3778,	3779,	3781,	3785,	3786,	3787,	3789,	3791,	3792,	3794,	3795,	3798,	3800,	3804,	3807,	3808,	3811,	3812,	3815,	3826,	3827,	3832,	3836,	3838,	3843,	3860,	3868,	3870,	3882,	3898,	3902,	3903,	3905,	3911,	3925,	3931,	3934,	3937,	3947,	3948,	3957,	3960,	3961,	3964,	3969,	3973,	3974,	3975,	3976,	3982,	3983,	3990,	3995,	3999,	4001,	4006,	4016,	4021,	4028,	4029,	4038,	4039,	4050,	4055,	4057,	4063,	4070,	4079,	4083,	4086,	4088,	4092,	4093,	4095,	4100,	4103,	4116,	4121,	4125,	4126,	4129,	4131,	4132,	4133,	4134,	4138,	4151,	4154,	4156,	4163,	4165,	4168,	4173,	4178,	4182,	4183,	4192,	4199,	4203,	4207,	4210,	4212,	4214,	4216,	4218,	4222,	4223,	4226,	4230,	4235,	4242,	4243,	4246,	4257,	4258,	4260,	4269,	4273,	4274,	4281,	4311,	4325,	4328,	4336,	4337,	4340,	4342,	4344,	4346,	4347,	4350,	4352,	4357,	4362,	4363,	4371,	4377,	4386,	4405,	4408,	4409,	4413,	4417,	4418,	4430,	4434,	4439,	4441,	4448,	4449,	4454,	4469,	4470,	4475,	4476,	4479,	4485,	4488,	4490,	4512,	4522,	4526,	4535,	4536,	4544,	4546,	4552,	4553,	4571,	4572,	4575,	4576,	4577,	4586,	4596,	4604,	4607,	4609,	4613,	4616,	4617,	4620,	4623,	4624,	4629,	4630,	4632,	4637,	4641,	4650,	4651,	4652,	4660,	4669,	4670,	4675,	4676,	4680,	4684,	4688,	4692,	4703,	4711,	4729,	4730,	4734,	4735,	4743,	4744,	4750,	4753,	4767,	4771,	4776,	4778,	4784,	4791,	4800,	4801,	4806,	4807,	4812,	4813,	4814,	4818,	4821,	4823,	4826,	4828,	4829,	4831,	4833,	4837,	4840,	4841,	4843,	4847,	4848,	4859,	4864,	4877,	4887,	4889,	4897,	4913,	4915,	4918,	4933,	4938,	4939,	4941,	4942,	4944,	4946,	4950,	4956,	4966,	4969,	4972,	4977,	4978,	4980,	4981,	4984,	4991,	4994,	5002,	5017,	5019,	5033,	5036,	5037,	5044,	5047,	5053,	5056,	5065,	5073,	5083,	5085,	5091,	5092,	5094,	5095,	5100,	5108,	5112,	5113,	5114,	5115,	5117,	5124,	5133,	5142,	5146,	5147,	5157,	5158,	5161,	5175,	5186,	5189,	5191,	5198,	5200,	5201,	5204,	5212,	5214,	5233,	5246,	5250,	5252,	5261,	5266,	5272,	5274,	5279,	5283,	5287,	5289,	5293,	5297,	5306,	5308,	5309,	5317,	5320,	5329,	5331,	5336,	5342,	5348,	5352,	5353,	5355,	5356,	5357,	5360,	5364,	5370,	5371,	5372,	5374,	5381,	5383,	5385,	5389,	5391,	5392,	5396,	5399,	5400,	5402,	5410,	5415,	5419,	5420,	5423,	5425,	5426,	5430,	5432,	5434,	5435,	5436,	5437,	5439,	5441,	5442,	5444,	5445,	5447,	5449,	5452,	5455,	5456,	5459,	5460,	5471,	5472,	5474,	5475,	5479,	5481,	5487,	5489,	5493,	5494,	5497,	5503,	5504,	5508,	5512,	5513,	5514,	5519,	5522,	5523,	5524,	5526,	5527,	5528,	5529,	5530,	5531,	5532,	5533,	5534,	5535,	5536,	5537,	5538,	5539,	5540,	5541,	5542,	5543,	5545,	5546,	5547,	5548,	5550,	5554,	5555,	5556,	5558,	5559,	5560,	5562,	5563,	5564,	5565,	5567,	5569,	5570,	5571,	5572,	5573,	5579,	5580,	5582,	5583,	5585,	5586,	5592,	5593,	5594,	5595,	5596,	5597,	5598,	5599,	5600,	5601,	5602,	5606,	5607,	5608,	5611,	5612,	5613,	5614,	5616,	5617,	5618,	5619,	5620,	5621,	5622,	5624,	5625,	5627,	5628,	5629,	5630,	5631,	5632,	5633,	5634,	5635,	5636,	5637,	5639,	5641,	5642,	5643,	5644,	5645,	5647,	5648,	5649,	5650,	5661,	5670,	5672,	5673,	5675,	5679,	5705,	5706,	5719,	5720,	5721,	5722,	5723,	5724,	5725,	5730,	5732,	5736,	5737,	5738,	5739,	5741,	5750,	5752,	5755,	5756,	5757,	5761,	5765,	5771,	5773,	5774,	5775,	5781,	5782,	5786,	5787,	5789,	5790,	5804,	5806,	5815,	5816,	5819,	5821,	5823,	5828,	5832,	5835,	5840,	5842,	5845,	5846,	5848,	5849,	5850,	5851,	5853,	5854,	5857,	5861,	5862,	5865,	5870,	5874,	5877,	5879,	5880,	5881,	5883,	5885,	5887,	5889,	5891,	5892,	5896,	5897,	5898,	5899,	5900,	5901,	5902,	5903,	5904,	5905,	5906,	5920,	5921,	5923,	5931,	5932,	5937,	5938,	5945,	5953,	5954,	5963,	5965,	5968,	5976,	5982,	5983,	5985,	5993,	5994,	5995,	5997,	5999,	6001,	6004,	6008,	6010,	6013,	6014,	6015,	6016,	6017,	6018,	6019,	6020,	6021,	6026,	6027,	6028,	6029,	6033,	6034,	6035,	6036,	6038,	6039,	6040,	6041,	6042,	6044,	6045,	6050,	6058,	6060,	6062,	6063,	6067,	6074,	6075,	6078,	6081,	6082,	6083,	6092,	6093,	6095,	6097,	6099,	6100,	6101,	6103,	6106,	6108,	6111,	6113,	6114,	6115,	6116,	6118,	6119,	6123,	6124,	6126,	6129,	6130,	6134,	6139,	6140,	6141,	6147,	6156,	6157,	6158,	6159,	6160,	6161,	6162,	6164,	6169,	6170,	6173,	6174,	6175,	6179,	6180,	6183,	6186,	6187,	6191,	6192,	6193,	6194,	6195]
    df.loc[clbr8, 'clbr'] = 8
    
    clbr9 = [2,	4,	5,	14,	30,	52,	62,	73,	79,	89,	95,	99,	101,	102,	110,	139,	162,	177,	178,	179,	182,	195,	200,	206,	214,	220,	222,	228,	230,	232,	234,	235,	239,	240,	243,	246,	250,	251,	255,	264,	265,	266,	273,	274,	289,	292,	293,	295,	296,	300,	301,	302,	303,	305,	310,	311,	314,	320,	323,	329,	334,	336,	339,	342,	343,	344,	347,	351,	353,	354,	357,	360,	364,	365,	368,	373,	391,	398,	406,	411,	415,	416,	420,	426,	427,	434,	435,	439,	442,	447,	465,	466,	499,	502,	509,	529,	548,	567,	569,	639,	675,	679,	713,	716,	743,	750,	756,	757,	764,	765,	771,	773,	778,	781,	792,	799,	855,	878,	880,	887,	889,	891,	895,	903,	905,	919,	978,	979,	982,	983,	984,	987,	988,	992,	994,	995,	997,	1056,	1080,	1094,	1122,	1125,	1129,	1132,	1139,	1140,	1141,	1144,	1168,	1224,	1230,	1296,	1297,	1312,	1342,	1380,	1389,	1396,	1432,	1438,	1439,	1440,	1441,	1442,	1443,	1445,	1446,	1448,	1449,	1450,	1455,	1456,	1458,	1460,	1463,	1464,	1465,	1466,	1468,	1469,	1473,	1475,	1476,	1478,	1479,	1480,	1481,	1483,	1484,	1485,	1486,	1489,	1490,	1491,	1492,	1494,	1495,	1499,	1500,	1501,	1502,	1503,	1505,	1506,	1507,	1508,	1509,	1510,	1511,	1512,	1513,	1514,	1516,	1517,	1518,	1527,	1537,	1541,	1543,	1545,	1557,	1562,	1563,	1576,	1580,	1583,	1585,	1593,	1594,	1597,	1609,	1616,	1643,	1652,	1673,	1682,	1688,	1691,	1703,	1707,	1763,	1767,	1769,	1778,	1782,	1813,	1826,	1840,	1844,	1861,	1870,	1871,	1876,	1877,	1878,	1888,	1903,	1950,	1980,	2046,	2055,	2057,	2058,	2063,	2064,	2067,	2070,	2071,	2072,	2073,	2082,	2083,	2084,	2088,	2089,	2093,	2095,	2099,	2104,	2105,	2109,	2110,	2111,	2114,	2115,	2117,	2122,	2123,	2128,	2132,	2141,	2149,	2158,	2166,	2177,	2226,	2255,	2280,	2291,	2296,	2303,	2331,	2350,	2357,	2361,	2363,	2370,	2378,	2389,	2390,	2395,	2396,	2408,	2417,	2418,	2426,	2430,	2444,	2449,	2450,	2452,	2457,	2458,	2462,	2463,	2470,	2475,	2481,	2485,	2493,	2494,	2509,	2530,	2539,	2544,	2549,	2554,	2569,	2572,	2575,	2579,	2589,	2599,	2607,	2614,	2619,	2620,	2622,	2624,	2632,	2640,	2645,	2649,	2656,	2659,	2664,	2676,	2684,	2685,	2696,	2699,	2702,	2719,	2721,	2722,	2729,	2731,	2735,	2740,	2746,	2749,	2752,	2765,	2776,	2777,	2780,	2782,	2785,	2800,	2805,	2811,	2815,	2823,	2863,	2884,	2894,	2896,	2926,	2947,	2956,	2985,	2989,	3012,	3030,	3055,	3077,	3080,	3092,	3108,	3112,	3138,	3142,	3150,	3159,	3163,	3175,	3176,	3196,	3198,	3212,	3213,	3216,	3217,	3222,	3224,	3236,	3239,	3243,	3259,	3263,	3271,	3272,	3279,	3288,	3291,	3297,	3320,	3332,	3340,	3346,	3347,	3348,	3349,	3350,	3353,	3354,	3355,	3371,	3378,	3379,	3389,	3393,	3400,	3401,	3402,	3405,	3410,	3411,	3414,	3415,	3416,	3419,	3422,	3425,	3428,	3429,	3431,	3434,	3437,	3477,	3480,	3481,	3483,	3487,	3489,	3490,	3494,	3496,	3499,	3500,	3503,	3504,	3507,	3509,	3514,	3517,	3518,	3521,	3530,	3531,	3541,	3560,	3564,	3566,	3569,	3570,	3573,	3574,	3581,	3593,	3596,	3597,	3602,	3604,	3619,	3637,	3638,	3640,	3641,	3642,	3643,	3645,	3646,	3652,	3655,	3662,	3669,	3670,	3676,	3678,	3679,	3680,	3688,	3690,	3699,	3701,	3703,	3711,	3716,	3717,	3727,	3728,	3736,	3737,	3741,	3743,	3747,	3750,	3756,	3759,	3765,	3769,	3771,	3780,	3784,	3797,	3802,	3809,	3847,	3879,	3888,	3891,	3901,	3906,	3910,	3912,	3921,	3942,	3946,	3978,	3987,	4000,	4003,	4005,	4020,	4035,	4046,	4051,	4056,	4073,	4102,	4107,	4140,	4141,	4150,	4153,	4162,	4164,	4189,	4202,	4219,	4225,	4237,	4238,	4241,	4245,	4253,	4262,	4270,	4279,	4287,	4291,	4299,	4304,	4307,	4315,	4319,	4321,	4333,	4370,	4379,	4399,	4414,	4415,	4419,	4443,	4451,	4499,	4501,	4509,	4513,	4528,	4563,	4565,	4582,	4600,	4605,	4614,	4627,	4643,	4656,	4657,	4661,	4678,	4727,	4733,	4748,	4749,	4757,	4760,	4762,	4766,	4768,	4775,	4790,	4792,	4820,	4824,	4845,	4858,	4869,	4875,	4880,	4917,	4940,	4947,	4957,	4962,	4965,	4967,	4971,	4976,	5008,	5042,	5064,	5082,	5084,	5086,	5090,	5099,	5105,	5107,	5118,	5128,	5143,	5155,	5166,	5183,	5235,	5236,	5254,	5260,	5276,	5277,	5280,	5286,	5291,	5294,	5295,	5299,	5302,	5310,	5312,	5323,	5349,	5365,	5367,	5375,	5376,	5390,	5395,	5422,	5443,	5446,	5450,	5454,	5458,	5490,	5498,	5500,	5510,	5525,	5549,	5553,	5575,	5576,	5577,	5578,	5581,	5584,	5587,	5588,	5589,	5590,	5603,	5610,	5665,	5709,	5729,	5748,	5766,	5793,	5802,	5831,	5834,	5841,	5847,	5878,	5888,	5890,	5893,	5894,	5907,	5910,	5912,	5914,	5915,	5916,	5917,	5919,	5925,	5927,	5928,	5934,	5935,	5941,	5942,	5943,	5946,	5947,	5948,	5956,	5957,	5958,	5959,	5960,	5964,	5967,	5969,	5973,	5974,	5979,	5981,	5986,	5987,	5988,	5990,	6006,	6012,	6068,	6090,	6102,	6121,	6122,	6138]
    df.loc[clbr9, 'clbr'] = 9
    
    clgr9 = [2,	102,	110,	125,	152,	179,	189,	195,	212,	221,	239,	243,	246,	261,	267,	310,	312,	333,	373,	388,	398,	406,	411,	415,	416,	420,	426,	427,	439,	442,	446,	447,	454,	459,	466,	474,	477,	478,	479,	483,	490,	500,	504,	510,	516,	524,	529,	530,	533,	548,	596,	626,	679,	754,	757,	759,	799,	855,	857,	863,	871,	880,	994,	995,	998,	1007,	1075,	1132,	1151,	1179,	1183,	1200,	1224,	1230,	1252,	1312,	1421,	1440,	1443,	1444,	1451,	1456,	1468,	1473,	1488,	1497,	1501,	1509,	1527,	1543,	1545,	1566,	1571,	1576,	1585,	1593,	1609,	1614,	1647,	1652,	1664,	1673,	1688,	1703,	1719,	1721,	1761,	1784,	1857,	1867,	1868,	1878,	1937,	1958,	1960,	1993,	2070,	2104,	2141,	2149,	2152,	2158,	2280,	2291,	2292,	2296,	2311,	2331,	2350,	2356,	2357,	2363,	2408,	2417,	2418,	2426,	2463,	2488,	2492,	2569,	2583,	2636,	2651,	2657,	2667,	2685,	2705,	2719,	2734,	2763,	2780,	2782,	2785,	2805,	2811,	2815,	2823,	2876,	2939,	2948,	2984,	2991,	3000,	3040,	3066,	3106,	3115,	3133,	3138,	3159,	3198,	3205,	3232,	3243,	3263,	3270,	3271,	3288,	3291,	3332,	3345,	3346,	3347,	3355,	3410,	3425,	3445,	3455,	3476,	3477,	3480,	3483,	3489,	3503,	3507,	3509,	3514,	3517,	3518,	3521,	3530,	3536,	3547,	3548,	3549,	3553,	3563,	3564,	3573,	3582,	3593,	3602,	3610,	3613,	3617,	3637,	3639,	3653,	3665,	3666,	3669,	3673,	3689,	3695,	3715,	3731,	3741,	3815,	3830,	3887,	3921,	3927,	4003,	4005,	4020,	4046,	4074,	4075,	4102,	4116,	4129,	4140,	4150,	4165,	4261,	4278,	4291,	4307,	4382,	4393,	4395,	4441,	4443,	4451,	4462,	4494,	4504,	4506,	4547,	4565,	4582,	4584,	4654,	4676,	4677,	4710,	4723,	4735,	4743,	4749,	4772,	4773,	4775,	4790,	4842,	4845,	4880,	4931,	4944,	4962,	4976,	4986,	5072,	5087,	5107,	5175,	5235,	5243,	5280,	5291,	5299,	5310,	5323,	5329,	5355,	5365,	5367,	5376,	5390,	5395,	5446,	5449,	5454,	5458,	5463,	5482,	5498,	5525,	5575,	5576,	5578,	5610,	5665,	5709,	5729,	5748,	5761,	5783,	5831,	5847,	5893,	5907,	5908,	5914,	5928,	5933,	5938,	5943,	5945,	5959,	5968,	5978,	5986,	6068,	6090,	6122,	6157,	6191]
    df.loc[clgr9, 'clgr'] = 9
    
    df['agediff'] = df['agebr'] - df['agegr']
    
    df_1 = df[(df['secmargr']==0) & (df['secmarbr']==0)]
    df_2 = df[df['secmargr']==0]
    df_3 = df[df['secmarbr']==0]
    df_filter = [df_1, df_2, df_3]
    
    form = ['~ post_mortality + post + rural + C(clbr) + C(clgr) + C(depc)', '~ post_mortality + post + rural + C(clgr) + C(depc)','~ post_mortality + post + rural + C(clbr) + C(depc)']
    group = [['post_mortality', 'post', 'rural', 'clbr', 'clgr', 'depc'],
            ['post_mortality', 'post', 'rural', 'clgr', 'depc'],
            ['post_mortality', 'post', 'rural', 'clbr', 'depc']]
    
    lst = ['agediff', 'agegr', 'agebr']

    i = 0
    
    for var in lst:
        df2 = df_filter[i]
        group_var = group[i]
        formula = var + form[i]
        group_var.append(var) 
        results = smf.ols(formula, data=df2).fit(cov_type = 'cluster', cov_kwds = {'groups': df2[group_var].dropna()['depc']})
        table_star = summary_col([results],stars=True).tables[0]   
        a = [] 
        a.append(int(results.nobs))
        b = table_star.loc['post_mortality':'R-squared',].to_numpy().tolist() + ['Yes', 'Yes', 'Yes'] + a
        b = list(flatten(b))
        b[9], b[6] =  b[6], b[9]
        table6_1.iloc[1:12, i] = b
        table6_1.iloc[8, 1] = 'No'
        table6_1.iloc[7, 2] = 'No'
        i += 1

    return table6_1


'''Table A5 (continue)'''
def table_a5_b(df):
    
    s = ('Class imputed', ' from background', ' characteristics')
    row_name = ['Dependent variable', 'panel B', 'Percent of soldiers killed x postwar', '', 'Percent of soldiers killed', '',
                'Postwar', '', 'Rural', '', 
                'Bride’s age (/100)', '', 'Groom’s Age (/100)', '', 'Groom class dummies', 
                'Département dummies', '$R^{2}$', 'Observations']

    table_a5_b = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: []}, orient='index').T
    table_a5_b[' '] = row_name
    table_a5_b = table_a5_b.set_index(' ')
    table_a5_b.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride']

    for ind in ['classdiff', 'mardn', 'lowbr', 'post_mortality', 'post', 'rural', 'agebrd', 'agegrd', 'est_clbr', 'est_clgr']:
        df[ind] = pd.to_numeric(df[ind], downcast='float')
    
    lst = ['classdiff', 'mardn', 'lowbr']

    i = 0 
    
    for var in lst:
        formula = var + "~ post_mortality + mortality + post + rural + agebrd + agegrd + C(est_clgr_half)"
        results = smf.ols(formula, data=df).fit(cov_type = 'cluster', cov_kwds = {'groups': df[[var, 'post_mortality', 'mortality', 
                                                                                                'post', 'rural', 'agebrd', 'agegrd', 'est_clgr_half', 'depc']].dropna()['depc']})
        table_star = summary_col([results],stars=True).tables[0]
            
        a = [] 
        a.append(int(results.nobs))
        b = table_star.loc['post_mortality':'R-squared',].to_numpy().tolist() + ['Yes', 'No'] + a
        b = list(flatten(b))
        b[12], b[13], b[14] = b[14], b[13], b[12]
        table_a5_b.iloc[2:18, i] = b
        i += 1
        
    return table_a5_b


'''Table 1: Statistic Summary'''
def summary_stats(d):

    df = d.copy()
    
    var_list = ['mortality', 'sr', 'sr_39', 'sr_49', 'agegr', 'agebr']
    sub_df = df[var_list]

    table1 = pd.DataFrame()
    table1 = sub_df.describe().T
    table1 = table1.astype(float).round(2)
    table1['Description'] = ["Military mortality rate", 
                             "Sex ratio (#18-59 males/ #15-49 females)", 
                             "Sex ratio (#males/ #females, aged 15-39)",
                             "Sex ratio (#males/ #females, aged 15-49)", 
                             "Groom's age",
                             "Bride's age"]
    table1['Variables'] = var_list
    table1 = table1.set_index('Variables')
    table1 = table1.rename(columns=str.title)
    table1 = table1[['Description', 'Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']]
    table1['Count'] = table1['Count'].map('{:,.0f}'.format)
    
    return table1


''' Table 5 - Panel A (Update IV results)'''
def table_5_b(df5_1, df5_2):
    
    s = (' Class ', 'defined by own', ' occupation ', ' Class  ', 'defined by father', ' occupation  ')
    row_name = ['Dependent variable', 'Panel A. Stage 2 regressions', 'Sex ratio (men/women)', '', 
                'Postwar', '', 'Rural', '', 'Bride’s age (/100)', '', 'Groom’s age (/100)', '', 
                'Groom class dummies', 'Département dummies']

    table_5_b = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: [], s[3]: [], s[4]: [], s[5]: []}, orient='index').T
    table_5_b[' '] = row_name
    table_5_b = table_5_b.set_index(' ')
    table_5_b.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride', 'Class difference', 'Married down', 'Low-class bride']
    lst = ['classdiff', 'mardn', 'lowbr']
    
    sample5_1 = df5_1.copy()
    
    '''Contruct sample'''
    
    sample5_1['id1'] = sample5_1.index + 1
    sample5_1_1 = pd.get_dummies(sample5_1[['clgr', 'depc']], prefix = ['clgr', 'depc'], columns=['clgr', 'depc'], drop_first = True) # Create dummy variables
    sample5_1_1['id2'] = sample5_1_1.index + 1
    sample5_1 = sample5_1.merge(sample5_1_1, left_on='id1', right_on='id2', how = 'outer')
    control1 = sample5_1.columns[-96:-1].tolist()
    
    sample5_2 = df5_2.copy()
        
    sample5_2['id1'] = sample5_2.index + 1
    sample5_2_1 = pd.get_dummies(sample5_2[['clfgr', 'depc']], prefix = ['clfgr', 'depc'], columns=['clfgr', 'depc'], drop_first = True) # Create dummy variables
    sample5_2_1['id2'] = sample5_2_1.index + 1
    sample5_2 = sample5_2.merge(sample5_2_1, left_on='id1', right_on='id2', how = 'outer')
    control2 = sample5_2.columns[-96:-1].tolist()

    i = 0
    df = [sample5_1, sample5_2]
    ct = [control1, control2]
    cl = [['depc_4', 'depc_57', 'depc_67', 'depc_90'], ['depc_4', 'depc_55', 'depc_57', 'depc_67', 'depc_90']]

    for k in [0, 1]:
        df_a = df[k]
        control = ct[k]
        collinearity = cl[k]
        for var in lst:
            
            if (var == 'mardn') & (k == 0):
                collinearity.append('clgr_7.0')  
            if (var == 'mardn') & (k == 1):   
                collinearity.append('clfgr_7.0')
                
            control = list(set(control) - set(collinearity)) 
            sample5_1 = df_a.drop(columns=collinearity) # drop variables causing collinearity
            var_1 = []
            var_1.append(var)
            df_5_1 = sample5_1[var_1 + ['post', 'rural', 'agebrd', 'agegrd', 'sr', 'post_mortality', 'depc'] + control].dropna()
            column_names = [var, 'sr', 'post', 'rural', 'agebrd', 'agegrd', 'post_mortality', 'depc'] + control
            df_5_1 = df_5_1.reindex(columns=column_names)
            df_5_1['cons'] = 1
    
            '''Run model'''

            ivmod = IV2SLS(df_5_1[var], df_5_1[['cons', 'post', 'rural', 'agebrd', 'agegrd'] + control], df_5_1.sr, df_5_1.post_mortality)
            res_2sls_std = ivmod.fit(cov_type='clustered', clusters=df_5_1.depc)
            iv_parameters = res_2sls_std.params.to_frame().loc[['sr', 'post', 'rural', 'agebrd', 'agegrd']]
            iv_pvalues = res_2sls_std.pvalues.to_frame().loc[['sr', 'post', 'rural', 'agebrd', 'agegrd']]
            
            b2 = iv_pvalues.to_numpy().tolist()
            b2 = list(flatten(b2))
            b2 = [round(num, 3) for num in b2]
            table_5_b.iloc[[3, 5, 7, 9, 11], i] = b2
            
            b1 = iv_parameters.to_numpy().tolist()
            b1 = list(flatten(b1))
            b1 = [round(num, 3) for num in b1]
            b1 = [str(x) for x in b1]

            for j in range(0, 5):
                if b2[j] < 0.01:
                    b1[j] = b1[j]+'***'
                elif (b2[j] >= 0.01) & (b2[j] < 0.05):
                    b1[j] = b1[j]+'**'
                elif (b2[j] >= 0.05) & (b2[j] < 0.1):
                    b1[j] = b1[j]+'*'
                
            b1 = b1 + ['Yes', 'Yes']
            table_5_b.iloc[[2, 4, 6, 8, 10, 12, 13], i] = b1
            
            i += 1
                
    return table_5_b


'''Table 5 - Panel B'''
def table_5_c(d1, d2):
    
    s = (' Class ', 'defined by own', ' occupation ', ' Class  ', 'defined by father', ' occupation  ')
    row_name = ['Dependent variable', 'Panel B. Stage 1 regressions', 'Percent of soldiers killed x postwar', '', 
                'Postwar', '', 'Rural', '', 'Bride’s age (/100)', '', 'Groom’s age (/100)', '', 
                'Groom class dummies', 'Département dummies', '$R^{2}$', 'Observations']

    table5_c = pd.DataFrame.from_dict({s[0]: [], s[1]: [], s[2]: [], s[3]: [], s[4]: [], s[5]: []}, orient='index').T
    table5_c[' '] = row_name
    table5_c = table5_c.set_index(' ')
    table5_c.loc['Dependent variable'] = ['Class difference', 'Married down', 'Low-class bride', 
                                          'Class difference', 'Married down', 'Low-class bride']
    
    lst = ['sr', 'sr', 'sr']
    
    df5_1 = d1.copy()
    df5_2 = d2.copy()
    sample = [df5_1, df5_2]
    v2 = ['clgr', 'clfgr']
    i = 0

    for k in [0, 1]:
        df_a = sample[k]
        var2 = v2[k]
        for var in lst:
            i += 1
            formula = "sr ~ post_mortality + post + rural + agebrd + agegrd + C(depc) + " + "C(" + var2 + ")"
            results = smf.ols(formula, data=df_a).fit(cov_type = 'cluster', cov_kwds = {'groups': df_a[['sr', 'post_mortality', 
                                                                                        'post', 'rural', 'agebrd', 'agegrd', var2, 'depc']].dropna()['depc']})
            table_star = summary_col([results],stars=True).tables[0]
            
            a = [] 
            a.append(int(results.nobs))
            b = table_star.loc['post_mortality':'R-squared',].to_numpy().tolist() + ['Yes', 'Yes'] + a
            b = list(flatten(b))
            b[10], b[11], b[12] = b[12], b[11], b[10]
            j = i - 1
            table5_c.iloc[2:16, j] = b

    return table5_c