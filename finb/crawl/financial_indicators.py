from collections import OrderedDict
import requests
from copy import deepcopy
from finb.utils.vn_lang import VN_COMBINE_ACCENT_REPLACE

# http://dulieu.mbs.com.vn/vi/Enterprise/FinancialIndicator?StockCode=PNJ
# https://www.bsc.com.vn/Companies/Profile/PNJ
# https://agriseco.com.vn/Companies/FinancialStatements/AAA
# http://ezsearch.fpts.com.vn/Services/EzData/Default2.aspx?s=465


def get_financial_indicators(symbol):
    npages = 20
    furl = f"http://api.dulieu.mbs.com.vn/api/Enterprise/GetFinanceBalanceSheet?stockCode={symbol}&reportTermType=2&unit=1&pageIndex=%d&pageSize=5&language=1&reportType=CSTC"

    payload = {}
    headers = {
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'Origin': 'http://dulieu.mbs.com.vn',
        'Referer': f'http://dulieu.mbs.com.vn/vi/Enterprise/FinancialIndicator?StockCode={symbol}',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    ret_dict = OrderedDict()
    for i in range(1, npages):
        url = furl % i
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        if data["Code"] != 200:
            break

        data_list = data["Data"]["DataList"]
        header_data_list = data["Data"]["HeaderDataList"]

        keys = []
        for item in header_data_list:
            quarter = int(item["TermCode"][1:])
            year = item["YearPeriod"]
            ret_dict[(quarter, year)] = []
            keys.append((quarter, year))

        for item in data_list:
            nvalues = len(keys)
            for j in range(1, nvalues+1):
                z = deepcopy(item)
                z["Name"] = item["Name"].replace("ngoại tệchưa", "ngoại tệ chưa")
                z["Name"] = z["Name"].replace("hoat động", "hoạt động")
                for k, v in VN_COMBINE_ACCENT_REPLACE.items():
                    z["Name"] = z["Name"].replace(k, v)

                ret_dict[keys[j-1]].append([z["Name"].strip(), item["Value%d" % j]])
    return ret_dict
