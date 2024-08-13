#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


#define a function to filter to onlyu significant features
def filter_significance(df, column=2, reverse_values=False, top_40=True):
    df = df.copy()
    #define the test column
    test = df.columns[column][:-5]
    print(f"Test column: {test}")
    
    df['whole_feature'] = df['Feature']
    
    split_features = df['Feature'].str.split(';')
    
    #keep the lowest label
    def extract_levels(split_features):
        features = []
        for feature in split_features:
            for level in reversed(feature):
                if level not in {'s__', 'g__', 'f__', 'o__', 'c__', 'p__'}:
                    features.append(level)
                    break
            else:
                features.append('N/A')  # If all levels are 's__', 'g__', etc.
        return features

    df['Feature'] = extract_levels(split_features)
    
    split_features = df['whole_feature'].str.split(';')
    
    # Split the "Feature" column at semicolon
    split_features = df['whole_feature'].str.split(';', expand=True)
    
    # Extract the second and last elements from the split result
    df['Phylum'] = split_features[1]

    # Move the "Phylum" column to the first position
    df = df[['Phylum'] + [col for col in df.columns if col != 'Phylum']]
        
    #Extract lower and upper confidence intervals 
    df['lower_hdi']= df[f'{test}_hdi'].str.extract(r'\((.*?),')[0].astype(float)
    df['upper_hdi'] = df[f'{test}_hdi'].str.extract(r'.*,(.*?)\)')[0].astype(float)
    
    # Select and rename columns
    df = df[['Phylum', 'Feature', f'{test}_mean', 'lower_hdi', 'upper_hdi']]
    
    df = df.rename(columns={f'{test}_mean': 'mean'})
    print(f"Total features before filtering: {len(df)}")
    
    # Filter rows to significant features
    df = df[(df['lower_hdi'] > 0) | (df['upper_hdi'] < 0)]
    print(f"Significant features: {len(df)}")
    
    #Reverse values if needed 
    if reverse_values == True:
        df_reversed = df.copy()
        df['mean'] = -df_reversed['mean']
        df['lower_hdi'] = -df_reversed['lower_hdi']
        df['upper_hdi'] = -df_reversed['upper_hdi']
        
    #Define neagtively and positively associated microbes
    df['Group'] = np.where(df['mean'] < 0, 'Bottom', 'Top')
    
    if top_40 == True:
        top_positive = df.nlargest(20, 'mean')
        top_negative = df.nsmallest(20, 'mean')
        df = pd.concat([top_positive, top_negative], ignore_index=True)
        print(f"Top Features: {len(top_positive)}")
        print(f"Bottom Features: {len(top_negative)}")
    
    else:
        top_positive = df[df['Group'] == "Top"]
        top_negative = df[df['Group'] == "Bottom"]
        df = pd.concat([top_positive, top_negative], ignore_index=True)
        print(f"Top Features: {len(top_positive)}")
        print(f"Bottom Features: {len(top_negative)}")
        
    df = df.sort_values(by="mean")
    
    return df, top_positive, top_negative


# In[3]:





# In[ ]:




