from collections import OrderedDict
import requests
from copy import deepcopy
from finb.utils.vn_lang import VN_COMBINE_ACCENT_REPLACE, check_eng_name
from unidecode import unidecode

def get_major_holders(symbol):
    url = f"https://www.bsc.com.vn/api/Data/Companies/MajorHolders?symbol={symbol}"

    payload = {}
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': f'https://www.bsc.com.vn/Companies/MajorHolders/{symbol}',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': 'ASP.NET_SessionId=dsfabbnc0t4pyk5f4xwjhuin; _fbp=fb.2.1600532504137.710301496; _ga=GA1.3.1235247621.1600532505; _culture=vi-VN; NSC_XfcTfswfs_443=ffffffff091da14845525d5f4f58455e445a4a42378b; _gid=GA1.3.1553636956.1601622104; _gat=1; TawkConnectionTime=0; NSC_XfcTfswfs_443=ffffffff091da14845525d5f4f58455e445a4a42378b'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    ret_dict = response.json()

    names = dict()

    for item in ret_dict:
        if item["Name"] not in names:
            names[unidecode(item["Name"])] = [item["Name"]]
        else:
            names[unidecode(item["Name"])].append(item["Name"])

    cs = set()
    for k, v in names.items():
        has_vn = 0
        for i, n in enumerate(v):
            if not check_eng_name(n):
                has_vn = i
                break
        cs.add(v[has_vn])

    ret_dict = list(filter(lambda x:x["Name"] in cs, ret_dict))

    return ret_dict
