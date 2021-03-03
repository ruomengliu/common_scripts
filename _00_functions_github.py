
import pandas as pd
import pandas.core.algorithms as algos
import numpy as np


# The in_df dataframe should contain only one cross-section.
# char is the characteristic to sort on.
# group is the intended number of bins to sort into.
# nyse is a binary variable that tells the function whether to use all or just NYSE firms to determine the bin edges/breakpoints.
# The function keeps the original dataframe intact, and adds a column that is by default named a+'_sort'

# Example:
# df is a panel dataframe of firm-month observations.
# To sort firms by date into quintiles by NYSE breakpoints on some characteristic a, do:
# df = df.groupby(['date']).apply(xs_CharSort, a, 5, nyse))
# df.reset_index(drop=True, inplace=True)


def xs_CharSort(in_df, char, group, nyse):
    df = in_df.copy()# I make this (deep) copy here so that I do not change the input dataframe.
    if nyse==True:
        U_bins = df[(pd.notnull(df[char])) & (df['exchcd']==1.0)].copy() # U_bins is used for getting breakpoints, or bin edges.
    else:
        U_bins = df[pd.notnull(df[char])].copy()
    try:
        bins = pd.qcut(U_bins[char], group, retbins=True)[1]
        bins[bins==bins.max()] = np.inf
        bins[bins==bins.min()] = -np.inf
        ranks = pd.cut(df[char], bins=bins, labels=range(1,group+1), include_lowest=True)
        df[char+'_sort'] = ranks
    except ValueError:
        # This is the case where pd.qcut cannot be directly applied due to non-unique bin edges. The rest of this function deals with this case.
        # get bins. Code here is from the source pd.qcut script.
        quantiles = np.linspace(0, 1, group+1)
        quantile_edges = algos.quantile(U_bins[char], quantiles)
        quantile_edges_unique = sorted(list(set(quantile_edges)))
        if len(quantile_edges_unique)<len(quantile_edges) and len(quantile_edges_unique)>1 and U_bins[char].nunique()>=group: # if bin edges are not unique, but there is enough heterogeneity in the characteristic value in the cross-section, then do the following.
            print(char+' on date '+df['date'].unique()[0]+' has non-unique bin edges.')
            d = dict(Counter(quantile_edges)) #d is a list of count how many times each bin edge appears.  
            dict_clusters = dict((k,v) for k,v in d.items() if v>1).items()
            U_rest = U_bins[~U_bins[char].isin([k for k,v in d.items() if v>1])].copy()
            counter=0
            while len(quantile_edges_unique)<len(quantile_edges) and len(quantile_edges_unique)>1 and group>1: # while there are clusters, and there are some heterogeneity in char value.
                if counter>0:
                    print(char+' on date '+df['date'].unique()[0]+' has more than one while set of clusters: counter='+str(counter))
                # Find out the values at which observations cluster, and assign cluster values to groups
                elif counter==0:
                    df['del_'+char+'_sort'] = np.nan # This column is necessary here because I will possibly modify it right below
                if U_rest[char].nunique()>group-len(dict_clusters): # if after taking out the cluster values, df still has enough unique char values left to sort into group-len(dict_clusters) number of bins, then do the following.
                    for cluster_value, times in dict_clusters:
                        indices = [i for i,x in enumerate(quantile_edges) if x==cluster_value] # indices is a list of bin edge indices that have cluster values in the bin edge list
                        if cluster_value==max(quantile_edges_unique):# If the cluster_value is the largest bin edge, then all values greater than cluster_value should go into the highest bin.
                            mask = (df[char]>=cluster_value) & (df['del_'+char+'_sort'].isnull())
                            df.loc[mask, 'del_'+char+'_sort'] = (indices[0]+1)*1000+times+group/100 
                        elif cluster_value==min(quantile_edges_unique):# If the cluster_value is the lowest bin edge, then all values greater than cluster_value should go into the lowest bin.
                            mask = (df[char]<=cluster_value) & (df['del_'+char+'_sort'].isnull())
                            df.loc[mask, 'del_'+char+'_sort'] = (indices[0]+1)*1000+times+group/100 
                        else:
                            df.loc[df[char]==cluster_value, 'del_'+char+'_sort'] = (indices[0]+1)*1000+times+group/100 # This line puts the cluster value into a bin by itself.
                    group = group-len(dict_clusters) # redefine group to be the group number needed after accounting for the clusters.
                    try:
                        bins = pd.qcut(U_rest[char], group, retbins=True)[1]
                        bins[bins==bins.max()] = np.inf
                        bins[bins==bins.min()] = -np.inf
                        ranks = pd.cut(df[char], bins=bins, labels=range(1,group+1), include_lowest=True)
                        df['del_'+char+'_sort_rest'] = ranks
                        df['del_'+char+'_sort'] = np.where(df['del_'+char+'_sort'].isnull(), df['del_'+char+'_sort_rest'], df['del_'+char+'_sort'])
                        # Now column del_char_sort contains the cluster bins and the rest of the bins. The next block relabel the bins in an ascending order.
                        df['del_sort_mean'] = df.groupby(['del_'+char+'_sort'])[char].transform('mean')
                        relabel = df.groupby(['del_'+char+'_sort'])[char].mean()
                        relabel.sort_values(inplace=True)
                        relabel.reset_index(drop=True, inplace=True)
                        relabel = pd.DataFrame(relabel).rename(columns={char:'del_sort_mean'})
                        relabel[char+'_sort'] = (relabel.index+1).astype(float)
                        df = pd.merge(df, relabel, how='left', on=['del_sort_mean'])
                        df.drop([i for i in df.columns.values if 'del_' in i], axis=1, inplace=True)
                        break
                    except ValueError:
                        quantiles = np.linspace(0, 1, group+1)
                        quantile_edges = algos.quantile(U_rest[char], quantiles)
                        quantile_edges_unique = sorted(list(set(quantile_edges)))
                        # print(quantile_edges, quantile_edges_unique, len(quantile_edges_unique)==len(quantile_edges))
                        d = dict(Counter(quantile_edges)) #d is a list of counts of how many times each bin edge appears.
                        dict_clusters = dict((k,v) for k,v in d.items() if v>1).items()
                        U_rest = U_rest[~U_rest[char].isin([k for k,v in d.items() if v>1])].copy()
                        U_bins = U_rest.copy()
                        counter+=1
                        continue
                else: # if there is insufficient cross-sectional heterogeneity in char values, then do not sort.
                    df[char+'_sort'] = np.nan
                    df.drop([i for i in df.columns.values if 'del_' in i], axis=1, inplace=True)
                    break
        else: # if there is only one value in quantile_edges_unqiue, then do not sort. This is the last of the situations that need to be addressed.
            # print(char+' on date '+df['date'].unique()[0]+' has insufficient cross-sectional heterogeneity in char values')
            df[char+'_sort'] = np.nan
    df[char+'_sort'] = df[char+'_sort'].astype(float)
    return df
