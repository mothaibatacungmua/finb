import os
import json
import pandas as pd
from datetime import datetime
from finb import PROJECT_PATH
from finb.crawl.history import get_history_price
from finb.crawl.events import get_company_events
from finb.crawl.snapshot import get_company_snapshot
from finb.crawl.income_statement import get_income_statement
from finb.crawl.balance_sheet import get_balance_sheet
from finb.crawl.cashflow import get_cash_flow
from finb.crawl.financial_indicators import get_financial_indicators
from finb.crawl.major_holders import get_major_holders
from finb.utils.date import str_to_ts


class CrawlCompanyProfile:
    def __init__(self, symbol):
        self.symbol = symbol
        self.symbol_dir = os.path.join(PROJECT_PATH, f"market/company/{symbol}")
        if not os.path.exists(self.symbol_dir):
            os.makedirs(self.symbol_dir)

    def get_price_history(self, start_date:str=None, end_date:str=None):
        if start_date is None:
            start_date = "2008-01-01"
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        df = get_history_price(
                self.symbol,
                _from=str_to_ts(start_date),
                to=str_to_ts(end_date))
        df.to_csv(os.path.join(self.symbol_dir, "price.csv"))

    def get_events(self):
        df_dict = get_company_events(self.symbol)

        events_dir = os.path.join(self.symbol_dir, "events")
        if not os.path.exists(events_dir):
            os.makedirs(events_dir)

        for k, v in df_dict.items():
            v["df"].to_csv(os.path.join(events_dir, f"{v['type']}.csv"), index=False)

    def get_latest_snapshot(self):
        ret = get_company_snapshot(self.symbol)

        if not os.path.exists(self.symbol_dir):
            os.makedirs(self.symbol_dir)

        with open(os.path.join(self.symbol_dir, "snapshot.json"), "w") as fobj:
            json.dump(ret, fobj)

    def get_income_statement(self, from_year=None, to_year=None):
        report_dict = get_income_statement(self.symbol, from_year, to_year)

        income_stat_dir = os.path.join(self.symbol_dir, "incomestat")
        if not os.path.exists(income_stat_dir):
            os.makedirs( income_stat_dir)

        for k, v in report_dict.items():
            df = pd.DataFrame(columns=["fields", "values"])

            for field, value in v:
                df = df.append({
                    "fields": field,
                    "values": value
                }, ignore_index=True)
            df.set_index("fields", inplace=True)
            df = df[~df.index.duplicated(keep='first')]
            df.to_csv(os.path.join(income_stat_dir, f"{k[1]}-Q{k[0]}.csv"))

    def get_balance_sheet(self, from_year=None, to_year=None):
        balance_sheet_dict = get_balance_sheet(self.symbol, from_year, to_year)

        balansheet_dir = os.path.join(self.symbol_dir, "balansheet")
        if not os.path.exists(balansheet_dir):
            os.makedirs(balansheet_dir)

        for k, v in balance_sheet_dict.items():
            df = pd.DataFrame(columns=["fields", "values"])

            for field, value in v:
                df = df.append({
                    "fields": field,
                    "values": value
                }, ignore_index=True)
            df.set_index("fields", inplace=True)
            df = df[~df.index.duplicated(keep='first')]
            df.to_csv(os.path.join(balansheet_dir, f"{k[1]}-Q{k[0]}.csv"))

    def get_cashflow(self, from_year=None, to_year=None):
        cashflow_dict = get_cash_flow(self.symbol, from_year, to_year)

        cashflow_dir = os.path.join(self.symbol_dir, "cashflow")
        if not os.path.exists(cashflow_dir):
            os.makedirs(cashflow_dir)

        for k, v in cashflow_dict.items():
            df = pd.DataFrame(columns=["fields", "values"])

            for field, value in v:
                df = df.append({
                    "fields": field,
                    "values": value
                }, ignore_index=True)
            df.set_index("fields", inplace=True)
            df = df[~df.index.duplicated(keep='first')]
            df.to_csv(os.path.join(cashflow_dir, f"{k[1]}-Q{k[0]}.csv"))

    def get_financial_indicators(self):
        fin_inds_dict = get_financial_indicators(self.symbol)
        financial_indicators_dir = os.path.join(self.symbol_dir, "fininds")

        if not os.path.exists(financial_indicators_dir):
            os.makedirs(financial_indicators_dir)

        for k, v in fin_inds_dict.items():
            df = pd.DataFrame(columns=["fields", "values"])
            for field, value in v:
                df = df.append({
                    "fields": field,
                    "values": value
                }, ignore_index=True)
            df.set_index("fields", inplace=True)
            df = df[~df.index.duplicated(keep='first')]
            df.to_csv(os.path.join(financial_indicators_dir, f"{k[1]}-Q{k[0]}.csv"))

    def get_major_holders(self):
        ret_dict = get_major_holders(self.symbol)

        df = pd.DataFrame(columns=["Name", "Position", "Shares", "Ownership", "Reported"])
        for item in ret_dict:
            df = df.append({
                "Name": item.get("Name"),
                "Position": item.get("Position"),
                "Shares": item.get("Shares"),
                "Ownership": item.get("Ownership"),
                "Reported": item.get("Reported")
            }, ignore_index=True)

        df.to_csv(os.path.join(self.symbol_dir, "major_holders.csv"), index=False)


if __name__ == "__main__":
    # pnj_crawler = CrawlCompanyProfile("PNJ")

    # pnj_crawler.get_events()
    # pnj_crawler.get_latest_snapshot()

    # pnj_crawler.get_income_statement()
    # pnj_crawler.get_balance_sheet()
    # pnj_crawler.get_cashflow()
    # pnj_crawler.get_financial_indicators()

    asm_crawler = CrawlCompanyProfile("ASM")

    asm_crawler.get_major_holders()