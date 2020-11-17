import scipy.stats as stats
import math
import pandas as pd
from finb.analyzer.factor import TechnicalFactors


def compute_returns(df, price_col="Close"):
    returns = (df[price_col] - df[price_col].shift(1)) / df[price_col].shift(1) * 100
    df_ret = returns.to_frame()
    df_ret.columns = ["Return"]
    df_ret.fillna(0, inplace=True)
    return df_ret


def compute_beta(market_returns, stock_returns, start_date=None, end_date=None):
    if start_date is not None:
        market_returns = market_returns.loc[start_date:]
        stock_returns = stock_returns.loc[start_date:]
    if end_date is not None:
        market_returns = market_returns.loc[:end_date]
        stock_returns = stock_returns.loc[:end_date]
    result = stats.linregress(stock_returns.Return, market_returns.Return)
    return result


def specific_risk(stock_risk, market_risk=None, beta=None):
    if market_risk:
        return math.sqrt(stock_risk*stock_risk - market_risk*market_risk)
    if beta:
        return math.sqrt(stock_risk*stock_risk(1-beta*beta))


def normal_return_test(df, col="Close"):
    returns = (df[col] - df[col].shift(1)) / df[col].shift(1) * 100
    returns = returns.iloc[1:]
    df_ret = returns.to_frame()
    df_ret.columns = ["Return"]

    return {
        "jb_stat": stats.jarque_bera(df_ret["Return"].values)[0],
        "shapiro_stat": stats.shapiro(df_ret["Return"].values)[0]
    }


def time_bar(df):
    return df


def volume_bar(df:pd.DataFrame,threshold=1e6):
    t = df["Volume"]
    ts = 0
    idx = []
    for i, x in enumerate(t):
        ts += x
        if ts >= threshold:
            idx.append(i)
            ts = 0
            continue
    df = df.copy().iloc[idx].drop_duplicates()
    return df


def dollar_bar(df:pd.DataFrame, threshold=1e12):
    t = df["Volume"]
    ts = 0
    idx = []
    for i, x in enumerate(t):
        ts += (df.iloc[i].Close + df.iloc[i].Low + df.iloc[i].High)/3 * x * 1000
        if ts >= threshold:
            idx.append(i)
            ts = 0
            continue
    df = df.copy().iloc[idx].drop_duplicates()
    return df
