import os
import pandas as pd
import datetime
from finb.utils.datahub import \
  read_considered_df, read_balance_sheet_with_year_range, read_income_statement_with_year_range
from finb.utils.visualize import generate_colors_pool
from finb import PROJECT_PATH


companies_df = read_considered_df()
list_symbols = companies_df.index.tolist()
list_symbols.sort()
industries = ["Tất cả"] + list(companies_df["industryName"].unique())
colors_pool = generate_colors_pool()

CACHING_PATH = os.path.join(PROJECT_PATH, "analyzer/ui/.cache")


def read_balance_sheet_with_cache(symbol):
  raw_df = None
  percent_df = None
  current_year = datetime.datetime.now().year
  raw_cache_path = os.path.join(CACHING_PATH, symbol, "raw_balance_sheet.csv")
  percent_cache_path = os.path.join(CACHING_PATH, symbol, "percent_balance_sheet.csv")

  if not os.path.exists(os.path.join(CACHING_PATH, symbol)):
    os.makedirs(os.path.join(CACHING_PATH, symbol))

  if os.path.exists(raw_cache_path):
    raw_df = pd.read_csv(raw_cache_path)
    raw_df.set_index("fields", inplace=True)
  if os.path.exists(percent_cache_path):
    percent_df = pd.read_csv(percent_cache_path)
    percent_df.set_index("fields", inplace=True)

  if raw_df is None or percent_df is None:
    raw_df, percent_df = read_balance_sheet_with_year_range(symbol, current_year - 5, current_year, "both")

    raw_df.to_csv(raw_cache_path)
    percent_df.to_csv(percent_cache_path)

  return raw_df, percent_df


def read_income_statement_with_cache(symbol):
  raw_df = None
  percent_df = None
  current_year = datetime.datetime.now().year
  raw_cache_path = os.path.join(CACHING_PATH, symbol, "raw_income_statement.csv")
  percent_cache_path = os.path.join(CACHING_PATH, symbol, "percent_income_statement.csv")

  if not os.path.exists(os.path.join(CACHING_PATH, symbol)):
    os.makedirs(os.path.join(CACHING_PATH, symbol))

  if os.path.exists(raw_cache_path):
    raw_df = pd.read_csv(raw_cache_path)
    raw_df.set_index("fields", inplace=True)
  if os.path.exists(percent_cache_path):
    percent_df = pd.read_csv(percent_cache_path)
    percent_df.set_index("fields", inplace=True)

  if raw_df is None or percent_df is None:
    raw_df, percent_df = read_income_statement_with_year_range(symbol, current_year - 5, current_year, "both")

    raw_df.to_csv(raw_cache_path)
    percent_df.to_csv(percent_cache_path)

  return raw_df, percent_df