import pandas as pd
import numpy as np
import datetime
from finb.utils.datahub import read_balance_sheet, read_income_statement, \
    read_cashflow, read_financial_indicators, read_price_df, read_major_holders
from finb.utils.date import current_quarter_and_year, prev_quarter
from finb.utils.constant import PAR_VALUE, TAX_RATE


def nanc(f):
    def inside(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            return np.nan
    return inside


class CompanyQuarterlyFundamentalFactors:
    def __init__(self, symbol, year:int=None, quarter:int=None, dont_load_prev=False, using_current_price=False):
        self.symbol = symbol
        if year is None or quarter is None:
            self.year, self.quarter = current_quarter_and_year()
        else:
            self.year = year
            self.quarter = quarter

        self.balansheet_df = read_balance_sheet(symbol, self.year, self.quarter)
        self.incomestat_df = read_income_statement(symbol, self.year, self.quarter)
        self.cashflow_df = read_cashflow(symbol, self.year, self.quarter)
        # self.fininds_df = read_financial_indicators(symbol, self.year, self.quarter)

        self.price_df = read_price_df(symbol)

        if self.quarter == 1:
            sd = datetime.datetime(year=year, month=1, day=1)
            ed = datetime.datetime(year=year, month=4, day=1)
        elif self.quarter == 2:
            sd = datetime.datetime(year=year, month=4, day=1)
            ed = datetime.datetime(year=year, month=7, day=1)
        elif self.quarter == 3:
            sd = datetime.datetime(year=year, month=7, day=1)
            ed = datetime.datetime(year=year, month=10, day=1)
        else:
            sd = datetime.datetime(year=year, month=10, day=1)
            ed = datetime.datetime(year=year+1, month=1, day=1)

        if not using_current_price:
            self.price_df = self.price_df[(self.price_df.index >= sd) & (self.price_df.index < ed)]

        self.prev_fund_factors = []

        if not dont_load_prev:
            prev_y = self.year
            prev_q = self.quarter
            for _ in range(4):
                prev_y, prev_q = prev_quarter(prev_y, prev_q)

                prev_fund_factor = CompanyQuarterlyFundamentalFactors(
                        self.symbol, year=prev_y, quarter=prev_q, dont_load_prev=True)
                self.prev_fund_factors.append(prev_fund_factor)

    @property
    @nanc
    def NumberOfShares(self):
        shares_equity = self.balansheet_df.loc["1. Vốn đầu tư của chủ sở hữu"]["values"]
        num_of_shares = shares_equity / PAR_VALUE
        return num_of_shares

    @property
    @nanc
    def BVPS(self):
        """ Book value """
        v = (self.balansheet_df.loc["TỔNG CỘNG TÀI SẢN"]["values"]-self.balansheet_df.loc["A. Nợ phải trả"]["values"])/self.NumberOfShares
        return v

    @property
    @nanc
    def MC(self):
        """ Market Capitalization"""
        return self.NumberOfShares * self.price_df.iloc[-1]["Close"]*1000

    @property
    @nanc
    def CCE(self):
        """ Cash and cash equivalents """
        return float(self.balansheet_df.loc["I. Tiền và các khoản tương đương tiền"]["values"])

    @property
    @nanc
    def TotalDebt(self):
        """ Short-term debt + Long-term debt"""
        return float(self.balansheet_df.loc["A. Nợ phải trả"]["values"])

    @property
    @nanc
    def TotalAsset(self):
        """ Short-term debt + Long-term debt"""
        return float(self.balansheet_df.loc["TỔNG CỘNG TÀI SẢN"]["values"])

    @property
    @nanc
    def EV(self):
        """ Enterprise Value """
        return self.MC + self.TotalDebt - self.CCE - self.balansheet_df.loc["II. Các khoản đầu tư tài chính ngắn hạn"]["values"]

    @property
    @nanc
    def CFO(self):
        """ Cash Flow From Operating Activities """
        return float(self.cashflow_df.loc["Lưu chuyển tiền thuần từ hoạt động kinh doanh"]["values"])

    @property
    @nanc
    def CFO2EV(self):
        return self.CFO/self.EV

    @property
    @nanc
    def EBIT(self):
        """Earnings Before Interest and Tax"""
        return self.incomestat_df.loc["15. Tổng lợi nhuận kế toán trước thuế (11)+(14)"]["values"] + \
               self.incomestat_df.loc["-Trong đó: Chi phí lãi vay"]["values"]

    @property
    @nanc
    def EBITDA(self):
        "Earnings Before Interest, Tax, Depreciation and Amortization"
        return self.EBIT + self.cashflow_df.loc["- Khấu hao TSCĐ"]["values"]

    @property
    @nanc
    def EBITDA2EV(self):
        "Earnings Before Interest, Tax, Depreciation and Amortization to Enterprise Value"
        return self.EBITDA/self.EV

    @property
    @nanc
    def Trailing12MonthEPS(self):
        return self.EPS + self.prev_fund_factors[0].EPS + self.prev_fund_factors[1].EPS + self.prev_fund_factors[2].EPS

    @property
    @nanc
    def Trailing12MonthPE(self):
        return self.price_df.iloc[-1].Close*1000 / self.Trailing12MonthEPS

    @property
    @nanc
    def NetBB(self):
        """Net buyback"""
        return -self.cashflow_df.loc["8. Cổ tức, lợi nhuận đã trả cho chủ sở hữu"]["values"] + \
              -self.cashflow_df.loc["2. Tiền chi trả vốn góp cho các chủ sở hữu, mua lại cổ phiếu của doanh nghiệp đã phát hành"]["values"] - \
             self.cashflow_df.loc["1. Tiền thu từ phát hành cổ phiếu, nhận vốn góp của chủ sở hữu"]["values"]

    @property
    @nanc
    def NetExtFin(self):
        """Net external Financing"""

        return self.NetBB + \
                -self.cashflow_df.loc["4. Tiền chi trả nợ gốc vay"]["values"] - \
                self.cashflow_df.loc["3. Tiền vay ngắn hạn, dài hạn nhận được"]["values"]

    @property
    @nanc
    def BB2P(self):
        """ Net buyback to market capitalization """
        return self.NetBB / self.MC

    @property
    @nanc
    def BB2EV(self):
        """ Net external financing to enterprise value"""
        return self.NetExtFin / self.EV

    @property
    @nanc
    def B2P(self):
        """ Book value to maket value"""
        return self.BVPS / (self.price_df.iloc[-1]["Close"]*1000)

    @property
    @nanc
    def OPL(self):
        """Operating Liablities"""
        return self.balansheet_df.loc["3. Phải trả người bán ngắn hạn"]["values"] + \
            self.balansheet_df.loc["4. Người mua trả tiền trước"]["values"] + \
            self.balansheet_df.loc["6. Phải trả người lao động"]["values"] + \
            self.balansheet_df.loc["7. Chi phí phải trả ngắn hạn"]["values"] + \
            self.balansheet_df.loc["10. Doanh thu chưa thực hiện ngắn hạn"]["values"] + \
            self.balansheet_df.loc["1. Vay và nợ thuê tài chính ngắn hạn"]["values"]

    @property
    @nanc
    def OPA(self):
        """Operating Assets"""
        return self.balansheet_df.loc["I. Tiền và các khoản tương đương tiền"]["values"] + \
                self.balansheet_df.loc["III. Các khoản phải thu ngắn hạn"]["values"] + \
                self.balansheet_df.loc["IV. Tổng hàng tồn kho"]["values"] + \
                self.balansheet_df.loc["I. Các khoản phải thu dài hạn"]["values"] + \
                self.balansheet_df.loc["II. Tài sản cố định"]["values"] + \
                self.balansheet_df.loc["1. Chi phí trả trước dài hạn"]["values"] + \
                self.balansheet_df.loc["VII. Lợi thế thương mại"]["values"] + \
                self.balansheet_df.loc["1. Chi phí sản xuất, kinh doanh dở dang dài hạn"]["values"] + \
                self.balansheet_df.loc["2. chi phí xây dựng cơ bản dở dang"]["values"]

    @property
    @nanc
    def NOA(self):
        """Net Operating Assets"""
        return self.OPA - self.OPL

    @property
    @nanc
    def CFROI(self):
        """ Cash flow from operations to net operating assets """
        return self.CFO/self.NOA

    @property
    @nanc
    def OL(self):
        """ Operating Leverage """
        return self.OPL/self.NOA

    @property
    @nanc
    def XF(self):
        """ Net external financing to net operating assets"""
        return self.NetExtFin/self.NOA

    @property
    @nanc
    def WC(self):
        """ Working capital """
        return self.balansheet_df.loc["A. Tài sản lưu động và đầu tư ngắn hạn"]["values"] - \
               self.balansheet_df.loc["A. Nợ phải trả"]["values"]

    @property
    @nanc
    def Revenue(self):
        """ Revenue (Sales) """
        return self.incomestat_df.loc["1. Tổng doanh thu hoạt động kinh doanh"]["values"]

    @property
    @nanc
    def S2EV(self):
        return self.Revenue / self.EV

    @property
    @nanc
    def GrossIncome(self):
        return self.incomestat_df.loc["5. Lợi nhuận gộp (3)-(4)"]["values"]

    @property
    @nanc
    def NetIncome(self):
        """ Net Operarting Profit After Tax """
        return self.incomestat_df.loc["19. Lợi nhuận sau thuế thu nhập doanh nghiệp (15)-(18)"]["values"]

    @property
    @nanc
    def DeltaNOPAT(self):
        return self.NetIncome - self.prev_fund_factors[0].NetIncome

    @property
    @nanc
    def DeltaNOA(self):
        return self.NOA - self.prev_fund_factors[0].NOA

    @property
    @nanc
    def DeltaSales(self):
        return self.Revenue - self.prev_fund_factors[0].Revenue

    @property
    @nanc
    def Profitability(self):
        return self.DeltaNOPAT/self.DeltaSales

    @property
    @nanc
    def Scalability(self):
        return self.DeltaSales/self.NOA

    @property
    @nanc
    def Growth(self):
        return self.DeltaSales/self.Revenue

    @property
    @nanc
    def RIC(self):
        return self.Profitability * self.Scalability

    @property
    @nanc
    def OtherInvestments(self):
        return self.cashflow_df.loc["5. Đầu tư góp vốn vào công ty liên doanh liên kết"]["values"] + \
            self.cashflow_df.loc["6. Chi đầu tư ngắn hạn"]["values"] + \
            self.cashflow_df.loc["7. Tiền chi đầu tư góp vốn vào đơn vị khác"]["values"]

    @property
    @nanc
    def DA(self):
        """ Depreciation & Amortization"""
        return self.cashflow_df.loc["- Khấu hao TSCĐ"]["values"]

    @property
    @nanc
    def FCFF(self):
        return self.NetIncome + self.DA - self.DeltaWC - self.CAPEX - self.OtherInvestments

    @property
    @nanc
    def FCFE(self):
        return self.FCFF + \
               (self.cashflow_df["3. Tiền vay ngắn hạn, dài hạn nhận được"]["values"] +
                self.cashflow_df["4. Tiền chi trả nợ gốc vay"]["values"] +
                self.cashflow_df["5. Tiền chi trả nợ thuê tài chính"]["values"]) - \
                self.cashflow_df["- Chi phí lãi vay"]["values"]*(1 - TAX_RATE)

    @property
    @nanc
    def RNOA(self):
        return self.NetIncome/self.NOA

    @property
    def EPS(self):
        return self.NetIncome/self.NumberOfShares

    @property
    @nanc
    def PE(self):
        return self.price_df.iloc[-1].Close*1000 / self.EPS

    @property
    @nanc
    def DeltaWC(self):
        return (self.WC - self.prev_fund_factors[0].WC)

    @property
    @nanc
    def DeltaXF(self):
        return (self.XF - self.prev_fund_factors[0].XF)

    @property
    @nanc
    def CAPEX(self):
        return -(self.cashflow_df.loc["1. Tiền chi để mua sắm, xây dựng TSCĐ và các tài sản dài hạn khác"]["values"] +
            self.cashflow_df.loc["2. Tiền thu từ thanh lý, nhượng bán TSCĐ và các tài sản dài hạn khác"]["values"])

    @property
    @nanc
    def DeltaCAPEX(self):
        return (self.CAPEX - self.prev_fund_factors[0].CAPEX)

    @property
    @nanc
    def DeltaOL(self):
        return self.OL - self.prev_fund_factors[0].OL

    @property
    @nanc
    def AccountsPayable(self):
        """ Accounts Payable """
        return self.balansheet_df.loc["3. Phải trả người bán ngắn hạn"]["values"] +\
                self.balansheet_df.loc["11. Phải trả ngắn hạn khác"]["values"]

    @property
    @nanc
    def COGS(self):
        "Cost of Goods Sold"
        return self.incomestat_df.loc["4. Giá vốn hàng bán"]["values"]

    @property
    @nanc
    def DPO(self):
        """Day payable outstanding"""
        return self.AccountsPayable / self.COGS * 365/4

    @property
    @nanc
    def AdminExp2S(self):
        """ Administrative Expense to Revenue"""
        return self.incomestat_df.loc["10. Chi phí quản lý doanh nghiệp"]["values"]/self.Revenue

    @property
    @nanc
    def SellExp2S(self):
        """ Selling expenses """
        return self.incomestat_df.loc["9. Chi phí bán hàng"]["values"]/self.Revenue

    @property
    @nanc
    def ROS(self):
        """ return on sales """
        return self.EBIT / self.Revenue


class TechnicalFactors:
    def __init__(self, symbol, year=None, quarter=None):
        self.symbol = symbol
        self.price_df = read_price_df(symbol)
        self.major_holders_df = read_major_holders(symbol)
        self.year, self.quarter = current_quarter_and_year()
        self.fund_factors = CompanyQuarterlyFundamentalFactors(symbol, year=year, quarter=quarter)

    def TotalVol(self, days=20, shift=0):
        s = len(self.price_df)-shift - days
        e = len(self.price_df)-shift
        return self.price_df.iloc[s:e]["Volume"].sum()

    def MajorHolderShares(self):
        return self.major_holders_df["Shares"].sum()

    def FreeFloatingShares(self):
        return self.fund_factors.NumberOfShares - self.MajorHolderShares()

    def FreeFloatingPercent(self):
        return self.FreeFloatingShares()/self.fund_factors.NumberOfShares

    def TotalVol2FreeFloating(self, days=20, shift=0):
        return self.TotalVol(days=days, shift=shift)/self.FreeFloatingShares()



if __name__ == "__main__":
    # qfactors = CompanyQuarterlyFundamentalFactors("PNJ", year=2020, quarter=2)
    # qfactors = CompanyQuarterlyFundamentalFactors("GMD", year=2020, quarter=2)

    symbol = "ASM"
    df = pd.DataFrame(columns=[
        "Quater", "S2EV", "CFO2EV", "EBITDA2EV",
        "Trailing12MonthEPS", "Trailing12MonthPE",
        "EPS", "P/E", "B2P", "CFROI", "BB2EV", "OL", "XF", "RNOA", "ROS",
        "DeltaWC", "DeltaXF", "DeltaCAPEX", "DeltaOL",
        "DPO", "AdminExp2S", "SellExp2S", "FCFF"])

    tqy = []
    cy = 2020
    cq = 2
    for y in range(2015, cy+1):
        for q in range(1, 5):
            if y < cy:
                tqy.append((q, y))
            else:
                if q <= cq:
                    tqy.append((q, y))
    tqy.append((None, None))

    for (quarter, year) in tqy:
        using_current_price = False
        if quarter is None or year is None:
            using_current_price = True
            quarter = 2
            year = 2020
        qfactors = CompanyQuarterlyFundamentalFactors(symbol, year=year, quarter=quarter, using_current_price=using_current_price)

        if using_current_price:
            quarter = "now"
            year = "now"
        df = df.append({
            "Quater": "%s-%s" % (str(year), str(quarter)),
            "S2EV": qfactors.S2EV,
            "CFO2EV": qfactors.CFO2EV,
            "EBITDA2EV": qfactors.EBITDA2EV,
            "Trailing12MonthEPS": qfactors.Trailing12MonthEPS,
            "Trailing12MonthPE": qfactors.Trailing12MonthPE,
            "EPS": qfactors.EPS,
            "P/E": qfactors.PE,
            "B2P": qfactors.B2P,
            "CFROI": qfactors.CFROI,
            "BB2EV": qfactors.BB2EV,
            "OL": qfactors.OL,
            "XF": qfactors.XF,
            "RNOA": qfactors.RNOA,
            "ROS": qfactors.ROS,
            "DeltaWC": qfactors.DeltaWC,
            "DeltaXF": qfactors.DeltaXF,
            "DeltaCAPEX": qfactors.DeltaCAPEX,
            "DeltaOL": qfactors.DeltaOL,
            "DPO": qfactors.DPO,
            "AdminExp2S": qfactors.AdminExp2S,
            "SellExp2S": qfactors.SellExp2S,
            "FCFF": qfactors.FCFF
        }, ignore_index=True)

    print(df.T)

    tfactors = TechnicalFactors(symbol, year=2020, quarter=2)

    x = []
    for i in range(10, 0, -1):
        x.append(tfactors.TotalVol2FreeFloating(10, shift=i))
        # break
    print("Free floating: %0.4f" % tfactors.FreeFloatingPercent())
    print(x)