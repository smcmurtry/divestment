
# coding: utf-8

# In[1]:

import pandas as pd
import re
from bs4 import BeautifulSoup
import urllib2
import json
import requests
from matplotlib import pyplot as plt
get_ipython().magic(u'matplotlib inline')


### Identifying Fossil Fuel Companies

# In[2]:

df = pd.DataFrame.from_csv("../data/cleaned_td_bond_data.csv")


# In[3]:

df.head()


# In[4]:

int_cols = ['n_units', 'cost', 'fair_value']
for i in df.index:
    for c in int_cols:
        n = int(df[c][i].replace(',',''))
        df.ix[i, c] = n


# In[5]:

df.head()


# In[6]:

df.to_csv('../data/td_bond_data_more_clean.csv')


##### Problem: How do I programatically determine which companies are fossil fuel companies?

# There are two elements to this:
# 1. I need a complete list of fossil fuel companies. The Carbon Underground list is widely used but it leaves out many corporations that don't have huge reserves but are still very problematic, such as TransCanada.
# 2. I need a reliable way to detect when a company from a fund report matches one from my blacklist. This is not trivial because of differences with Inc., etc.

### 1. Compiling a Blacklist

##### Carbon Underground

# A list of the top 100 coal companies, and top 100 oil and gas companies, ranked by the carbon content of their reserves. http://fossilfreeindexes.com/research/the-carbon-underground/

# In[8]:

def rm_special_chr(s):
    for c in '.,-!@#$%^&*()<>[]{}\|;:?/`~+=-_':
        s = s.replace(c, '')
    s = s.replace('  ', ' ')
    return s

def str_clean(s):
    s = rm_special_chr(s)
    s = s.lower()
    words = set(s.split(' '))
    words.discard('inc')
    words.discard('lp')
    words.discard('llc')
    words.discard('ltd')
    words.discard('')
    return words


# In[9]:

df_coal = pd.DataFrame.from_csv('../data/carbon_underground_coal.csv', index_col=None)
df_oil_and_gas = pd.DataFrame.from_csv("../data/carbon_underground_oil_and_gas.csv", index_col=None)
coal_comps = set(df_coal['Coal Companies'])
oil_and_gas_comps = set(df_oil_and_gas['Oil and Gas Companies'])
carbon_underground = list(coal_comps.union(oil_and_gas_comps))
carbon_underground_clean= []
for corp in carbon_underground:
    element = str_clean(corp)
    element.discard('')
    carbon_underground_clean.append(element)


# In[10]:

carbon_underground_df = pd.DataFrame(carbon_underground, index=range(len(carbon_underground)), columns=['name'])


# In[11]:

carbon_underground_df.to_csv('../data/carbon_underground_all.csv')


##### Casting the net wider

# I should scrape the company names from this site: https://www.ic.gc.ca/eic/site/cis-sic.nsf/eng/00060.html

# In[12]:

urls = {'pipeline_transportation': 'http://www.ic.gc.ca/app/ccc/sld/cmpny.do?lang=eng&profileId=1921&naics=486',
        'oil_and_gas_extraction': 'http://www.ic.gc.ca/app/ccc/sld/cmpny.do?lang=eng&profileId=1921&naics=211',
        'coal_mining':'http://www.ic.gc.ca/app/ccc/sld/cmpny.do?lang=eng&profileId=1921&naics=2121'}


# In[13]:

def create_soup(url):
    html_doc = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html_doc)
    return soup

def get_corp_names(soup):
    corp_names = []
    company_list = soup.find_all("ul", class_="companyList")
    list_entries = company_list[0].find_all('li')
    for entry in list_entries:
        if entry.attrs == {'class': ['companyLinks']}: continue
        corp_names.append(entry.contents[0].replace('\n', '').replace('\t', '')[3:])
    return corp_names


# In[14]:

all_corp_names = []
for k in urls:
    soup = create_soup(urls[k])
    corp_names = get_corp_names(soup)
    all_corp_names += corp_names


# In[15]:

ca_gov_names = pd.DataFrame(all_corp_names, columns=['names'])
ca_gov_names.to_csv("../data/ca_gov_names.csv")


# In[16]:

ca_gov_names = pd.DataFrame.from_csv("../data/ca_gov_names.csv")


# In[17]:

ca_gov_corps_clean = []
for company in list(ca_gov_names.names):
    company_clean = str_clean(company)
    ca_gov_corps_clean.append(company_clean)


# In[18]:

ca_gov_corps_clean[:10]


##### Let's try using the corporate watch api

# documentation: http://api.corpwatch.org/documentation/api_examples.html

# In[19]:

def get_corp_url(year, company_name, limit):
    "get api request url from the corpwatch api"
    api_key = '2605d59c5b9f72946f6efc75cc2dccf9'
    url = 'http://api.corpwatch.org/' + str(year) + '/companies.json?company_name='
    parsed_name = ''
    for c in company_name:
        if c == ' ': 
            parsed_name += '+'
        else: 
            parsed_name += c
    url += parsed_name
    url += '&limit=' + str(limit)
    url += '&key=' + api_key
    return url

def get_sector_corpwatch(company_name):
    """Search for a company_name using the corpwatch api. If successful returns a tuple
    of the matched name and the industry.""" 
    results_limit = 1
    year = 2015
    u = get_corp_url(year, company_name, results_limit)
    response = requests.get(u)
    json_data = json.loads(response.text)
    try:
        results = json_data['result']['companies']
    except:
        return None, None
    if json_data['meta']['success'] != 1 or len(results) != 1:
        print 'oh no!'
        return None, None
    r = results.values()[0]
    return r['company_name'], r['industry_name']


# In[20]:

get_sector_corpwatch('pfizer')


# In[21]:

get_sector_corpwatch('barrick')


# In[22]:

get_sector_corpwatch('enbridge')


# In[23]:

get_sector_corpwatch('Husky Energy')


# In[24]:

get_sector_corpwatch('TransCanada')


# In[25]:

get_sector_corpwatch('kinder morgan')


### 2. Determining string similarity

# This is for the ca_gov list and the carbon underground list, since the corpwatch api performs its own search on their servers. The ca_gov list is small for now, but I may add names from other sources.

# In[26]:

from nltk.metrics import distance as dist
a = 'Suncor Energy Inc.'
b = 'Suncor Energy '
c = 'xyz wf'
d = 'Husky Energy'
e = ''


# In[27]:

print dist.edit_distance(a, b)
print dist.edit_distance(a, c)
print dist.edit_distance(a, d)
print dist.edit_distance(a, e)
print dist.edit_distance('BP LP', 'BP')


# This is okay, but it would probably be a better search if it looked at the number of matched words (not case-sensitive). It could return the ratio of matched words to unmatched words. 

### 3. Classifying the TD Bond Fund List

# In[28]:

df['fossil'] = pd.Series(index=df.index)


# In[29]:

len(df.organization)


# In[30]:

len(set(df.organization))


# In[31]:

class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}
    def __call__(self, *args):
        if not args in self.memo:
            self.memo[args] = self.f(*args)
        return self.memo[args]
    
def get_fossil_severity(company_name):
    cleaned_name = str_clean(company_name)
    if cleaned_name in carbon_underground_clean:
        return 3
    elif cleaned_name in ca_gov_corps_clean:
        return 2
    else:
        matched_name, sector = get_sector_corpwatch(company_name)
        print company_name + ', ' + str(matched_name) + ', ' + str(sector)
        if sector and sector in set([u'Crude petroleum & natural gas', u'Natural gas transmission']):
            return 1
        else:
            return 0
        
get_fossil_severity = Memoize(get_fossil_severity)


# In[147]:

for i in df.index:
    df.ix[i, 'fossil'] = 0
    if df.meta_cat[i] == 'CORPORATE BONDS ':
        df.ix[i, 'fossil'] = get_fossil_severity(df.organization[i])


# In[148]:

fossil = df.query("fossil != 0")['cost'].sum()
total = df['cost'].sum()
print float(fossil)/total


# In[149]:

total


# In[150]:

fossil


# In[151]:

df.query("fossil != 0")


# In[ ]:

