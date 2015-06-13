
# coding: utf-8

# In[1]:

import pandas as pd
from nltk.metrics import distance as dist


# In[2]:

carbon_underground_all = pd.DataFrame.from_csv('../data/carbon_underground_all.csv')
blacklist = list(set(carbon_underground_all.name))


# In[3]:

df_bond = pd.DataFrame.from_csv('../data/td_bond_data_more_clean.csv')
bond_companies = list(set(df_bond.organization))


# I need to find the longest string from this name that matches with a string

# The plan here is to determine a match based on how many of the characters from the search company matched a string in the blacklist. To do this correctly, I need to remove capitalization, remove special characters, and remove the abbreviations like inc, ltd, etc.

# In[4]:

def clean(s):
    "Removes special characters from a string, makes lower case, and removes common abbreviations."
    for c in '.,!@#$%^&*()<>[]{}\|;:?/`~+=-_': s = s.replace(c, '')
    s = s.lower()
    for abbr in ['inc', 'lp', 'llc', 'ltd', 'limited', 'corporation', 'holdings']: s = s.replace(abbr, '')
    # remove starting or trailing whitespace
    while s[0] == ' ': s = s[1:]
    while s[-1] == ' ': s = s[:-1]
    return s

def get_match(substr, blacklist):
    "If successful, returns a matched company"
    for x in blacklist:
        if substr in x: return x
    return None

def long_substr_3(company, blacklist):
    "Returns the longest substring from company that matches with any substring from an element of blacklist"
    substr = ''
    matched_company = ''
    for i in range(len(company)):
        for j in range(i+1, len(company)+1):
            if len(company[i:j]) > len(substr):
                fossil_company = get_match(company[i:j], blacklist)
                if fossil_company: 
                    substr = company[i:j]
                    matched_company = fossil_company
    return substr, matched_company

def is_match(unknown_company, blacklist_company, substr):
    """Takes the cleaned company name, as well as the substring from the name that matches
    a company in the cleaned blacklist, tells us if we have a match"""
    threshold = 0.4
    matched_fraction_a = 1. * len(substr) / len(unknown_company)
    matched_fraction_b = 1. * len(substr) / len(blacklist_company)
    if matched_fraction_a > threshold and matched_fraction_b > threshold: 
        return matched_fraction_a, matched_fraction_b
    return False, False


# In[5]:

blacklist_clean_1 = [clean(c) for c in blacklist]
for comp in bond_companies:
    comp = clean(comp)
    substr, matched_company = long_substr_3(comp, blacklist_clean_1)
    matched_fraction_a, matched_fraction_b = is_match(comp, matched_company, substr)
    if matched_fraction_a and matched_fraction_b:
        print comp + ', ' + substr + ', ' + str(matched_fraction_a) + ', ' + str(matched_fraction_b) + ', ' + matched_company


# This approach works quite well, and by increasing the threshold to around 0.8 I could return a list of only the truly matching companies.
# 
# There is one issue though: this approach would not work if there was even a single type in a name, or if there was added whitespace between words. Another thing this approach doesn't take advantage of is that when we have a match, it's almost always the case that all the words are present in both the company name and the matching entry in the blacklist (except for low-significance words like limited, inc, etc which are sometimes omitted).
# 
# I can probably improve the matching algorithm, but it's unclear at this point whether I need to or not. I'm not sure how likely it is I will have to deal with typos...
# 
# Who am I kidding? I will run into typos, even in fund reports, and I should be able to still match these companies.
# 
# I will look at an approach that splits the strings into an ordered list of words, and then match these lists to those in the blacklist. There will be an edit distance threshold (edit distance as a fraction of word length) for a word to match. All (or most?) words will need to match for the company to be a match. I will have to have a dictionary of abbreviations to make sure I match short forms and long forms.

# The Carbon Underground list has all of the corporate abbreviations removed. I'll start by trying this since it seems like it simplifies the identification process (I no longer need to worry about transforming 'limited liability corporation' into 'llc' and matching based on that).

# In[6]:

abbr2remove = set(['inc', 'incorporated', 'corporation', 'holding', 'holdings', 'hld', 'hldg',
                   'limited', 'ltd', 'limited liability corporation', 'llc'])


# In[7]:

def clean_2(company_name):
    "Takes a company name and returns an ordered list of lower case words with no special characters"
    for c in '.,!@#$%^&*()<>[]{}\|;:?/`~+=-_': company_name = company_name.replace(c, '')
    company_name = company_name.lower()
    for abbr in abbr2remove: company_name = company_name.replace(abbr, '')
    company_name = company_name.split(' ')
    clean_name = []
    for w in company_name:
        if w != '':
            while w[0] == ' ': w = w[1:]
            while w[-1] == ' ': w = w[:-1]
            if w != '': clean_name.append(w)
    return clean_name


# In[9]:

for c in blacklist[:10]:
    print c, clean_2(c)


# Whatever approach I use to determine if an initially unknown company is present on my blacklist, it must:
# * preserve word order. e.g. 'Canadain Natural Resources' should not match 'Natural Resources Canada'
# * should account for word length. e.g. similarity('enbridgw','enbridge') should be greater than similarity('bf', 'bp')
# 
# Here are the steps I've come up with:
# * for a company name (ordered list of words) to match, go through each entry in the blacklist and find the edit distince between corresponding words
# * this can be done as follows: assume unknown_corp = [a1, a2] and blacklist_entry = [b1, b2, b3, b4]. I should find the 'sameness' (based on  edit distance, between 0 and 1) for each possible superposition of words: [a2==b1, a1==b1 & a2==b2, a1==b2 & a2==b3, a1==b3 & a2==b4, a1==b4].
# * then I can find which superposition results in the best match (maybe this is just the sum of the sameness scores for each combination)
# * then I can make up some threshold for the total sameness (maybe debends on the number of words? maybe some generic words (like canadian, or pipeline, would be identified and would count for less?)

# In[10]:

def on_blacklist(unknown_corp, blacklist):
    "takes an unknown corporation name and returns True if the corporation is on the blacklist."
    on_blacklist = False
    blacklist = [clean_2(x) for x in blacklist]
    unknown_corp = clean_2(unknown_corp)
    for x in blacklist:
        name_sameness()
    return on_blacklist


# def name_sameness(name_a, name_b):
#     "takes two names and returns a score (0<=score<=1). 0 for totally dissimilar and 1 for identical."
#     
#     word_difference(name_a[-1], name_b[0])
#     
#     
#     # len(name_a) == 4, len(name_b) == 5
#     # number of iterations == 8
#     
#     
#     (-1,0)
#     
#     (-2,0) + (-1,1)
#     
#     (-3,0) + (-2,1) + (-1,2)
#     
#     (-4,0) + (-3,1) + (-2,2) + (-1,3)
#     
#              (-4,1) + (-3,2) + (-2,3) + (-1, 4)
#         
#                       (-4,2) + (-3,3) + (-2, 4)
# 
#                                (-4,3) + (-3, 4)
#                 
#                                         (-4, 4)
#         
#     
#     return score

# In[11]:

def name_sameness(name_a, name_b):
    "takes two names and returns a score (0<=score<=1). 0 for totally dissimilar and 1 for identical."
    n_iterations = len(name_a) + len(name_b) - 1
    
    for n in range(n_iterations):
        f()
    
    return score


# In[12]:

def word_difference(word_a, word_b):
    """Takes two words and returns a score (0<=difference_score). 
    0 for identical, and increasing for words that are less similar."""
    edit_distance = dist.edit_distance(word_a, word_b)
    difference_score = 1. * edit_distance / len(word_a)
    return difference_score


# In[15]:

word_difference('bp', 'bpa')


# In[16]:

word_difference('enbridga', 'enbridge')


# In[17]:

