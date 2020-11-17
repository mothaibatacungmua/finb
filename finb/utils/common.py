import os
import pandas as pd
from finb import PROJECT_PATH
import unidecode


def cafef_company_url(symbol):
    companies_df = pd.read_csv(os.path.join(PROJECT_PATH, "market/companies.csv"), index_col="symbol")

    name = companies_df.loc[symbol]["company"]

    unaccented_name = unidecode.unidecode(name).strip().lower()

    return "-".join(unaccented_name.split())



