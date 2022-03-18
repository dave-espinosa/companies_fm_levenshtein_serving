# # EXTRACT PARENT COMPANY BASED ON COMPANY BRANCHES
#
# Created by: Agustina Dinamarca & 1Mentor Inc.
#
# Developer: Agustina Dinamarca

# # LIBRARIES

import Levenshtein
import re
from nltk.corpus import stopwords

# # Special Functions:
#
# Developer: Agustina D.
# Version 1: 17/03/2022

# -----------------------------------------------------------------------------

# COMPANIES NAMES - FUZZY MATCHING WITH LEVENSHTEIN

# -----------------------------------------------------------------------------


def clean_query(query:list):
    """
    Cleaning of company names from a list of companies
    
    Parameters
    ----------
    
    query : list
        List of company names
    
    Returns
    -------
    
    query_cleaned : list
        List of company names cleaned
        
    """
    patterns = r"""[!+?:"\,<>\\(){}@%$#=*/[/-]"""
    stpwrds = stopwords.words('spanish') + stopwords.words('english')
    query_lst = [re.sub(patterns, " ", q.lower()) for q in query]
    query_lst = [[x for x in q.split() if x not in stpwrds] for q in query_lst]
    query_cleaned = [' '.join(w for w in q) for q in query_lst]
    return query_cleaned


def apply_fuzzy_matching_levenshtein(df, query:list, topk=5):
    """
    Applies fuzzy-matching (Levenshtein) to a query of company names to find the main name of the companies
    
    Parameters
    ----------
    
    df : Pandas DataFrame
        Company names dictionary dataframe
        
    query : list
        List of company names
    
    topk : int (default=5)
        Number of the most probable matches to return per company name
        
    Returns
    -------
    
    results: list
        List of topk results per company name
    
    """
    query_cleaned = clean_query(query)
    results = []
    for i in range(len(query)):
        df_filtered = df[df["alternate_title"].isin([query_cleaned[i]] + query_cleaned[i].split())].copy()
        if not df_filtered.empty:
            df_filtered['accuracy'] = 100 * df_filtered['alternate_title'].apply(lambda x: Levenshtein.ratio(query_cleaned[i], x))
            df_best_match = df_filtered.nlargest(topk, 'accuracy').round(2)
            best_results = df_best_match[['realName', 'accuracy']].to_dict('records')
        else:
            best_results = [{'realName':'NOT FOUND', 'accuracy': 0}]
        
        results.append(
            {
                'name': query[i],
                'realName': best_results[0]['realName'],
                'accuracy': best_results[0]['accuracy'],
                'topk': best_results
            }
        )
    return results