import os
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List
from finb import PROJECT_PATH
from finb.crawl.sectors import get_all_stock_company
from finb.crawl.company_profile import CrawlCompanyProfile
from finb.utils.date import convert_quarter_to_end_date


def read_price_df(symbol, renew=False):
	try:
		path = os.path.join(PROJECT_PATH, "market/company", symbol, "price.csv")
		if not os.path.exists(path) or renew:
			CrawlCompanyProfile(symbol).get_price_history()
		df = pd.read_csv(path, index_col=0, parse_dates=True)
		df.index.name = 'Date'

		x = datetime.now() - timedelta(hours=24+15)
		if df.index[-1] <= x:
			CrawlCompanyProfile(symbol).get_price_history()
			df = pd.read_csv(path, index_col=0, parse_dates=True)
			df.index.name = 'Date'
		return df
	except Exception as e:
		print("[read_price_df] Warning: ", str(e))

	return None


def generate_weekly_quotes(df):
	df_copy = df.copy()
	dates = df_copy.index.to_series()
	df_copy["Date"] = dates
	df_copy["Week"] = df_copy["Date"] - pd.to_timedelta(df_copy["Date"].dt.dayofweek, unit='d')

	cols = ["Week", "Open", "High", "Low", "Close", "Volume"]
	df_w = pd.DataFrame(columns=cols)

	for w in df_copy.Week.unique():
		df_iw = df_copy[df_copy["Week"] == w]
		open_w = df_iw.iloc[0]["Open"]
		high_w = df_iw["High"].max()
		low_w = df_iw["Low"].min()
		close_w = df_iw.iloc[-1]["Close"]
		vol_w = df_iw["Volume"].sum()

		df_w.loc[-1] = [w, open_w, high_w, low_w, close_w, vol_w]
		df_w.index = df_w.index + 1
		df_w = df_w.sort_index()

	df_w.set_index("Week", inplace=True)
	df_w = df_w.iloc[::-1]
	return df_w


def read_companies_df(filter_delisted=True):
	try:
		companies_csv = os.path.join(PROJECT_PATH, "market/companies.csv")
		if not os.path.exists(companies_csv):
			get_all_stock_company(companies_csv)

		companies_df = pd.read_csv(companies_csv)
		companies_df.set_index("symbol", inplace=True)
		if filter_delisted:
			companies_df = companies_df[companies_df['delistedDate'].isnull()]
		return companies_df
	except Exception as e:
		print("[read_companies_df] Warning ", str(e))
	return None


def read_considered_df():
	""" Note: To make considered df, run notebooks/Filter_By_MarketCap.ipynb """
	considered_csv_path = os.path.join(PROJECT_PATH, "market/considered.csv")
	if not os.path.exists(considered_csv_path):
		return None

	considered_df = pd.read_csv(considered_csv_path)
	considered_df.set_index("symbol", inplace=True)

	return considered_df


def read_snapshot(symbol):
	snapshot_path = os.path.join(PROJECT_PATH, "market/company", symbol, "snapshot.json")
	with open(snapshot_path) as fobj:
		ret = json.load(fobj)
	return ret


def read_balance_sheet(symbol, year, quarter, format="raw") -> [pd.DataFrame, List[pd.DataFrame]]:
	if convert_quarter_to_end_date(year, quarter) >= datetime.now():
		if format == "both":
			return None, None
		return None
	try:
		balance_sheet_path = os.path.join(
			PROJECT_PATH, "market/company", symbol, "balansheet", f"{year}-Q{quarter}.csv")

		if not os.path.exists(balance_sheet_path):
			CrawlCompanyProfile(symbol).get_balance_sheet(from_year=year-1, to_year=year+1)

		df = pd.read_csv(balance_sheet_path, header=0)
		df.set_index("fields", inplace=True)
		df.fillna(0, inplace=True)

		if format == "raw":
			return df
		# return percent format
		asset_first_row = df.index.to_list().index("A. Tài sản lưu động và đầu tư ngắn hạn")
		total_assset_row = df.index.to_list().index("TỔNG CỘNG TÀI SẢN")

		total_asset = df.loc["TỔNG CỘNG TÀI SẢN"]["values"]
		percent_df = pd.DataFrame(columns=["fields", "values"])
		percent_df = percent_df.append({"fields": "TÀI SẢN", "values": None}, ignore_index=True)

		for z in range(asset_first_row, total_assset_row+1):
			percent_df = percent_df.append({
				"fields": df.index[z],
				"values": df.iloc[z]["values"]/total_asset
			}, ignore_index=True)
		percent_df = percent_df.append({"fields": "NGUỒN VỐN", "values": None}, ignore_index=True)

		capital_first_row = df.index.to_list().index("A. Nợ phải trả")
		total_capital_row = df.index.to_list().index("TỔNG CỘNG NGUỒN VỐN")
		for z in range(capital_first_row, total_capital_row+1):
			percent_df = percent_df.append({
				"fields": df.index[z],
				"values": df.iloc[z]["values"]/total_asset
			}, ignore_index=True)

		percent_df.set_index("fields", inplace=True)
		percent_df.fillna(0, inplace=True)
		if format == "percent":
			return percent_df

		return df, percent_df

	except Exception as e:
		print("[read_balance_sheet] Warning ", str(e))
		if format == "both":
			return None, None
	return None


def read_balance_sheet_with_year_range(symbol, from_year, to_year, format="raw"):
	list_raw_df = []
	list_percent_df = []

	index = None
	for y in range(from_year, to_year+1):
		for q in range(1, 5):
			if format == "raw":
				df = read_balance_sheet(symbol, year=y, quarter=q, format=format)
				list_raw_df.append((f"{y}-Q{q}", df))
				if df is not None and index is None:
					index = df.index
			elif format == "percent":
				percent_df = read_balance_sheet(symbol, year=y, quarter=q, format=format)
				list_percent_df.append((f"{y}-Q{q}", percent_df))
				if percent_df is not None and index is None:
					index = percent_df.index
			else:
				df, percent_df = read_balance_sheet(symbol, year=y, quarter=q, format=format)
				if df is not None and index is None:
					index = df.index
				list_raw_df.append((f"{y}-Q{q}",df))
				list_percent_df.append((f"{y}-Q{q}",percent_df))

	def concat_raw_df():
		ret_raw_df = pd.DataFrame()
		ret_raw_df["fields"] = index
		for (q, df) in list_raw_df:
			if df is not None:
				ret_raw_df[q] = df["values"].tolist()
			else:
				ret_raw_df[q] = ""
		ret_raw_df.set_index("fields", inplace=True)
		return ret_raw_df

	def concat_percent_df():
		ret_raw_df = pd.DataFrame()
		ret_raw_df["fields"] = index
		for q, df in list_percent_df:
			if df is not None:
				ret_raw_df[q] = df["values"].tolist()
			else:
				ret_raw_df[q] = ""
		ret_raw_df.set_index("fields", inplace=True)
		return ret_raw_df

	if format == "raw":
		return concat_raw_df()

	if format == "percent":
		return concat_percent_df()

	return concat_raw_df(), concat_percent_df()


def read_income_statement(symbol, year, quarter, format="raw"):
	if convert_quarter_to_end_date(year, quarter) >= datetime.now():
		if format == "both":
			return None, None
		return None
	try:
		income_statement_path = os.path.join(
			PROJECT_PATH, "market/company", symbol, "incomestat", f"{year}-Q{quarter}.csv")

		if not os.path.exists(income_statement_path):
			CrawlCompanyProfile(symbol).get_income_statement(from_year=year-1, to_year=year+1)

		df = pd.read_csv(income_statement_path, header=0)
		df.set_index("fields", inplace=True)
		df.fillna(0, inplace=True)

		if df.loc["1. Tổng doanh thu hoạt động kinh doanh"]["values"] < df.loc["3. Doanh thu thuần (1)-(2)"]["values"]:
			df.loc["1. Tổng doanh thu hoạt động kinh doanh"]["values"] = df.loc["3. Doanh thu thuần (1)-(2)"]["values"] + \
																		 df.loc["2. Các khoản giảm trừ doanh thu"]["values"]

		if format == "raw":
			return df
		percent_df = pd.DataFrame(columns=["fields", "values"])
		first_row = df.index.to_list().index("1. Tổng doanh thu hoạt động kinh doanh")
		last_row = df.index.to_list().index("21. Lợi nhuận sau thuế của cổ đông của công ty mẹ (19)-(20)")
		revenue = df.loc["1. Tổng doanh thu hoạt động kinh doanh"]["values"]

		for z in range(first_row, last_row+1):
			percent_df = percent_df.append({
				"fields": df.index[z],
				"values": df.iloc[z]["values"]/revenue
			}, ignore_index=True)
		percent_df.set_index("fields", inplace=True)
		if format == "percent":
			return percent_df
		return df, percent_df
	except Exception as e:
		print("[read_income_statement] Warning ", str(e))

	return None

def read_income_statement_with_year_range(symbol, from_year, to_year, format="raw"):
	list_raw_df = []
	list_percent_df = []

	index = None
	for y in range(from_year, to_year+1):
		for q in range(1, 5):
			if format == "raw":
				df = read_income_statement(symbol, year=y, quarter=q, format=format)
				list_raw_df.append((f"{y}-Q{q}", df))
				if df is not None and index is None:
					index = df.index
			elif format == "percent":
				percent_df = read_income_statement(symbol, year=y, quarter=q, format=format)
				list_percent_df.append((f"{y}-Q{q}", percent_df))
				if percent_df is not None and index is None:
					index = percent_df.index
			else:
				df, percent_df = read_income_statement(symbol, year=y, quarter=q, format=format)
				if df is not None and index is None:
					index = df.index
				list_raw_df.append((f"{y}-Q{q}",df))
				list_percent_df.append((f"{y}-Q{q}",percent_df))

	def concat_raw_df():
		ret_raw_df = pd.DataFrame()
		ret_raw_df["fields"] = index
		for (q, df) in list_raw_df:
			if df is not None:
				ret_raw_df[q] = df["values"]
			else:
				ret_raw_df[q] = ""
		return ret_raw_df

	def concat_percent_df():
		ret_raw_df = pd.DataFrame()
		ret_raw_df["fields"] = index
		for q, df in list_raw_df:
			if df is not None:
				ret_raw_df[q] = df["values"]
			else:
				ret_raw_df[q] = ""
		return ret_raw_df

	if format == "raw":
		return concat_raw_df()

	if format == "percent":
		return concat_percent_df()

	return concat_raw_df(), concat_percent_df()


def read_cashflow(symbol, year, quarter):
	if convert_quarter_to_end_date(year, quarter) >= datetime.now():
		return None
	try:
		cashflow_path = os.path.join(
			PROJECT_PATH, "market/company", symbol, "cashflow", f"{year}-Q{quarter}.csv")

		if not os.path.exists(cashflow_path):
			CrawlCompanyProfile(symbol).get_cashflow(from_year=year-1, to_year=year+1)

		df = pd.read_csv(cashflow_path, header=0)
		df.set_index("fields", inplace=True)
		df.fillna(0, inplace=True)

		if df.loc["Lưu chuyển tiền thuần từ hoạt động kinh doanh"]["values"] == 0:
			df.loc["Lưu chuyển tiền thuần từ hoạt động kinh doanh"] = \
				df.loc["3. Lợi nhuận từ hoạt động kinh doanh trước thay đổi vốn lưu động"]["values"] + \
				df.loc["- Tăng, giảm các khoản phải thu"]["values"] + \
				df.loc["- Tăng, giảm hàng tồn kho"]["values"] + \
				df.loc["- Tăng, giảm các khoản phải trả (Không kể lãi vay phải trả, thuế thu nhập doanh nghiệp phải nộp)"]["values"] + \
				df.loc["- Tăng giảm chi phí trả trước"]["values"] +\
				df.loc["- Tăng giảm tài sản ngắn hạn khác"]["values"]+\
				df.loc["- Tiền lãi vay phải trả"]["values"]+\
				df.loc["- Thuế thu nhập doanh nghiệp đã nộp"]["values"]+\
				df.loc["- Tiền thu khác từ hoạt động kinh doanh"]["values"]+\
				df.loc["- Tiền chi khác từ hoạt động kinh doanh"]["values"]
		return df
	except Exception as e:
		print("[read_cashflow] Warning ", str(e))

	return None


def read_financial_indicators(symbol, year, quarter):
	try:
		financial_indicators_path = os.path.join(
			PROJECT_PATH, "market/company", symbol, "fininds", f"{year}-Q{quarter}.csv")

		if not os.path.exists(financial_indicators_path):
			CrawlCompanyProfile(symbol).get_financial_indicators()

		df = pd.read_csv(financial_indicators_path, header=0)
		df.set_index("fields", inplace=True)

		return df
	except Exception as e:
		print("[read_financial_indicators] Warning ", str(e))

	return None


def read_major_holders(symbol):
	major_holders_path =  os.path.join(
		PROJECT_PATH, "market/company", symbol, "major_holders.csv")
	if not os.path.exists(major_holders_path):
		CrawlCompanyProfile(symbol).get_major_holders()

	df = pd.read_csv(major_holders_path)

	return df


def get_same_industry(symbol, using_considered=True):
	if using_considered:
		filter_df = pd.read_csv(os.path.join(PROJECT_PATH, "market/considered.csv"))
	else:
		filter_df = read_companies_df()
	filter_df.set_index("symbol", inplace=True)

	industry_name = filter_df.loc[symbol].industryName
	df = filter_df[filter_df["industryName"] == industry_name]

	return df

