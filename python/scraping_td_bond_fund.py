
# coding: utf-8

# TD Bond Index fund annual report downloaded from here: http://quote.morningstar.ca/quicktakes/fund/f_ca.aspx?t=F0CAN05NFT

# In[1]:

import pdfminer
import numpy as np
import re
import pandas as pd
import collections


# In[3]:

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

def convert_pdf_to_txt(path, pagenos):
    "from: http://stackoverflow.com/questions/26748788/extraction-of-text-from-pdf-with-pdfminer-gives-multiple-copies"
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    #pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


# In[4]:

text = convert_pdf_to_txt("../data/td_bond_annual_repor.pdf", set([6]))


# In[5]:

text = {}
for pg in np.arange(6, 30):
    text[pg] = convert_pdf_to_txt("../data/td_bond_annual_repor.pdf", set([pg]))


# In[6]:

ctext = convert_pdf_to_txt("../data/td_bond_annual_repor.pdf", set(np.arange(5, 19)))


# In[7]:

sctext = ctext.split('\n')
counter=collections.Counter(sctext)


# In[8]:

lines2remove = []
for k in counter:
    if counter[k] > 1: lines2remove.append(k) 


# In[9]:

lines2remove


# In[10]:

lines2remove = set(lines2remove).difference(['                          Bank of Montreal'])


# In[11]:

sctext_2 = []
for ln in sctext:
    if len(set([ln]).intersection(lines2remove)) == 0:
        sctext_2.append(ln)


# In[12]:

print len(sctext), len(sctext_2)


# In[13]:

re.split(r'[ \t]{2,}', sctext_2[2])


# I want to get this into the format:
# org, n_units, interest_rate, due_date, cost, fair_value
# 
# units: none, number, %, date, \$, \$

# In[14]:

df = pd.DataFrame(index=range(len(sctext_2)), 
                  columns=['meta_cat', 'organization', 'n_units', 'description', 'cost', 'fair_value'])
                  #columns=['organization', 'n_units', 'interest_rate', 'due_date', 'cost', 'fair_value'])


# In[15]:

org = ''
meta_cat = ''
n = 0
for i, ln in enumerate(sctext_2[:-107]):
    ln_contents = re.split(r'[ \t]{2,}', ln)
    # the first element should be ''
    if len(ln_contents) == 5:
        # ln is a data line
        df.ix[n, 'meta_cat'] = meta_cat
        df.ix[n, 'organization'] = org
        df.ix[n, 'n_units'] = ln_contents[1]
        df.ix[n, 'description'] = ln_contents[2]
        df.ix[n, 'cost'] = ln_contents[3]
        df.ix[n, 'fair_value'] = ln_contents[4]
        n += 1
    elif len(ln_contents) == 2:
        if re.match('.*(?i)bonds', ln_contents[1]):
            abc = ln_contents[1].split('\xe2\x80\x93')
            meta_cat = abc[0]
#         if ln_contents[1] in set(['CORPORATE BONDS']):
#             print 'meta', ln_contents
        # ln is a category line
        org = ln_contents[1]
    elif len(ln_contents) == 1:
        if len(set(ln_contents).intersection(set([str(x) for x in np.arange(6, 19)]))) > 0:
            #print 'pg #', ln_contents
            continue
        else:
            # ln is the second line of an organization name mostly
            # org = ln_contents[0]
            # print 'a', ln_contents
            org += ln_contents[0]
    else:
        print n, ln_contents


# add this manually: 
# CORPORATE BONDS ' , BMO Capital Trust II
# '87,000', 'Callable 10.221% due December 31, 2018', '87,000', '113,720'
# 
# FEDERAL BONDS & GUARANTEES , Broadcast Centre Trust
# 0 ['', '488,610', '7.53% due May 01, 2027', '$', '550,534 $', '617,067']

# In[16]:

df.ix[n, 'meta_cat'] = 'CORPORATE BONDS '
df.ix[n, 'organization'] = 'BMO Capital Trust II'
df.ix[n, 'n_units'] = '87,000'
df.ix[n, 'description'] = 'Callable 10.221% due December 31, 2018'
df.ix[n, 'cost'] = '87,000'
df.ix[n, 'fair_value'] = '113,720'
n += 1


# In[17]:

df.ix[n, 'meta_cat'] = 'FEDERAL BONDS & GUARANTEES '
df.ix[n, 'organization'] = 'Broadcast Centre Trust'
df.ix[n, 'n_units'] = '488,610'
df.ix[n, 'description'] = '7.53% due May 01, 2027'
df.ix[n, 'cost'] = '550,534'
df.ix[n, 'fair_value'] = '617,067'
n += 1


# In[18]:

n


# In[19]:

df_2 = df[:n].copy()


# In[20]:

set(df_2.meta_cat)


# In[21]:

df_2.head()


# In[22]:

df_2.to_csv('../data/cleaned_td_bond_data.csv')


# In[ ]:

