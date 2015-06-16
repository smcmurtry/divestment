
# coding: utf-8

# In[1]:

import pandas as pd
import json


# In[2]:

df1 = pd.DataFrame.from_csv("../web/cu_coal_headquarters.csv")
df2 = pd.DataFrame.from_csv("../web/cu_oil_and_gas_headquarters.csv")


# In[3]:

df1['type'] = ['Coal']*len(df1)
df2['type'] = ['Oil & Gas']*len(df2)
del df2['oil_Gt_CO2']
del df2['gas_Gt_CO2']


# In[4]:

df3 = df1.append(df2, ignore_index=True)
df3.to_csv('../web/cu_joined.csv')


# In[5]:

def push_row(root, df, i, ident):
    for c1 in root["children"]:
        if c1['name'] == df.headquarters[i]:
            # country already exists
            for c2 in c1['children']:
                if c2['name'] == df.type[i]:
                    # type already exists
                    c2['children'].append({'id': ident, 'name': df.name[i], 'size': df.total_Gt_CO2[i]})
                    ident = ident + 1
                    return root, ident
            # type does not exist yet
            c1['children'].append({'id': ident, 'name': df.type[i], 'children': [{'id': ident+1, 'name': df.name[i], 'size': df.total_Gt_CO2[i]}]})
            ident = ident + 2
            return root, ident
    # country doesn't exist yet
    root['children'].append({ 'id': ident, 'name': df.headquarters[i], 'children': [{ 'id': ident + 1, 'name': df.type[i], 'children': [{'id': ident + 2, 'name': df.name[i], 'size': df.total_Gt_CO2[i]}] }] })
    ident = ident + 3
    return root, ident


# In[6]:

root = {'name': 'top', 'children':[]}
ident = 0
for i in df3.index:
    root, ident = push_row(root, df3, i, ident)


# In[7]:

f = open('../web/cu_data_3.json', 'w')
f.write(json.dumps(root))
f.close()


# In[8]:

def push_row_2(root, df, i, ident):
    for c1 in root["children"]:
        if c1['name'] == df.headquarters[i]:
            # country already exists
            c1['children'].append({'id': ident, 'name': df.name[i], 'type': df.type[i], 'size': df.total_Gt_CO2[i]})
            ident = ident + 1
            return root, ident
    # country doesn't exist yet
    root['children'].append({ 'id': ident, 'name': df.headquarters[i], 'children': 
                             [{ 'id': ident + 1, 'type': df.type[i], 'name': df.name[i], 'size': df.total_Gt_CO2[i]}] })
    ident = ident + 2
    return root, ident


# In[9]:

root = {'name': 'top', 'children':[]}
ident = 0
for i in df3.index:
    root, ident = push_row_2(root, df3, i, ident)


# In[10]:

f = open('../web/cu_data_4.json', 'w')
f.write(json.dumps(root))
f.close()


# In[14]:

