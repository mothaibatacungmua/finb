import os
from finb.utils.datahub import read_considered_df
from finb import PROJECT_PATH
companies_df = read_considered_df()
list_symbols = companies_df.index.tolist()
list_symbols.sort()
industries = ["Tất cả"] + list(companies_df["industryName"].unique())


CACHING_PATH = os.path.join(PROJECT_PATH, "analyzer/ui/.cache")