import os
import pandas as pd
import requests
import json
from finb import PROJECT_PATH
from tqdm import tqdm
from finb.crawl.company_profile import CrawlCompanyProfile


def get_all_stock_company(save_csv=None):
  url = "https://finfo-api.vndirect.com.vn/stocks?status=all"

  stocks = requests.get(url).json()
  df = pd.DataFrame(columns=['symbol', 'company', 'companyName', 'status', 'listedDate', 'delistedDate', 'floor', 'industryName'])

  i = 0
  for c in stocks.get("data", []):
    if c['object'] != "stock":
      continue

    row = [
      c['symbol'],
      c['company'],
      c['companyName'],
      c['status'],
      c.get('listedDate', ''),
      c.get('delistedDate', ''),
      c['floor'],
      c.get('industryName', '')
    ]
    df.loc[i] = row
    i += 1

  df.set_index("symbol", inplace=True)

  if save_csv is None:
    save_csv = os.path.join(PROJECT_PATH, "market/companies.csv")
  df.to_csv(save_csv)
  return df


def filter_companies_by_vol_and_mc():
  companies_csv = os.path.join(PROJECT_PATH, "market/companies.csv")
  if not os.path.exists(companies_csv):
    get_all_stock_company(companies_csv)
  companies_df = pd.read_csv(companies_csv)
  companies_df.set_index("symbol", inplace=True)
  companies_df = companies_df[companies_df['delistedDate'].isnull()]

  with tqdm(total=len(companies_df)) as pbar:
    for symbol, r in companies_df.iterrows():
      crawler = CrawlCompanyProfile(symbol)
      try:
        crawler.get_latest_snapshot()
      except:
        continue
      pbar.update(1)
  filter_df = pd.DataFrame(columns=['symbol', 'Market_Capital', '10-day_Average_Volume'])
  for symbol, r in companies_df.iterrows():
    symbol_dir = os.path.join(PROJECT_PATH, "market/company", symbol)

    if os.path.exists(symbol_dir):
      snapshot_path = os.path.join(PROJECT_PATH, "market/company", symbol, "snapshot.json")
      with open(snapshot_path) as fobj:
        snapshot = json.load(fobj)
      try:
        row = {
          "symbol": symbol,
          "Market_Capital": float(snapshot["Market_Capital"]),
          "10-day_Average_Volume": float(snapshot["10-day_Average_Volume"])}
        filter_df = filter_df.append(row, ignore_index=True)
      except:
        continue
  filter_df = filter_df[(filter_df["Market_Capital"] > 150 * 1e9) & (filter_df["10-day_Average_Volume"] > 1e4)]
  filter_df.set_index("symbol", inplace=True)
  filter_df.to_csv(os.path.join(PROJECT_PATH, "market/considered.csv"))


if __name__ == "__main__":
  get_all_stock_company()
  filter_companies_by_vol_and_mc()