from collections import OrderedDict
import requests
from urllib3.exceptions import InsecureRequestWarning
from copy import deepcopy
from finb.utils.date import current_quarter_and_year
from finb.utils.vn_lang import VN_COMBINE_ACCENT_REPLACE

# http://dulieu.mbs.com.vn/vi/Enterprise/FinancialIndicator?StockCode=PNJ
# https://www.bsc.com.vn/Companies/Profile/PNJ
# https://agriseco.com.vn/Companies/FinancialStatements/AAA
# http://ezsearch.fpts.com.vn/Services/EzData/Default2.aspx?s=465

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
def get_cash_flow(symbol, from_year=None, to_year=None):
    furl = f"https://www.bsc.com.vn/api/Data/Finance/LastestFinancialReports?symbol={symbol}&type=4&year=%d&quarter=4&count=5"

    payload = {}
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': f'https://www.bsc.com.vn/Companies/FinancialStatements/{symbol}',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'ASP.NET_SessionId=dsfabbnc0t4pyk5f4xwjhuin; _fbp=fb.2.1600532504137.710301496; _ga=GA1.3.1235247621.1600532505; _gid=GA1.3.1484322541.1600532505; _culture=vi-VN; NSC_XfcTfswfs_443=ffffffff091da14945525d5f4f58455e445a4a42378b; _gat=1; TawkConnectionTime=0; NSC_XfcTfswfs_443=ffffffff091da14945525d5f4f58455e445a4a42378b'
    }

    ret_dict = OrderedDict()
    _, cr_year = current_quarter_and_year()

    if from_year is None and to_year is None:
        from_year = cr_year - 15
        to_year = cr_year + 1
    elif from_year is None:
        from_year = cr_year - 15
    elif to_year is None:
        to_year = cr_year + 1

    for year in range(from_year, to_year):
        url = furl % year
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        data = response.json()

        if data is None:
            continue

        tmp_dict = OrderedDict()

        for item in data:
            name = item["Name"]
            for k, v in VN_COMBINE_ACCENT_REPLACE.items():
                name = name.replace(k, v).strip()
            values = item["Values"]
            for x in values:
                quarter = x["Quarter"]
                year = x["Year"]
                rv = x["Value"]
                if (quarter, year) in tmp_dict:
                    tmp_dict[(quarter, year)].append([name, rv])
                else:
                    tmp_dict[(quarter, year)] = [[name, rv]]

        for k, v in tmp_dict.items():
            if k not in ret_dict:
                ret_dict[k] = v

    return ret_dict

if __name__ == "__main__":
    print(get_cash_flow("HBC"))