import requests
import pandas as pd


def dividend_event(e):
    return [
        e["type"],
        e["typeDesc"],
        e["effectiveDate"],
        e["disclosuredDate"],
        e["expiredDate"],
        e["content"],
        e.get("dividend", ""),
        e["ratio"],
        e.get("actualDate", ""),
        e.get("divPeriod", ""),
        e.get("divYear", ""),
        e.get("numberOfShares", "")
    ]


def meeting_event(e):
    return [
        e["type"],
        e["typeDesc"],
        e["effectiveDate"],
        e["disclosuredDate"],
        e["content"]
    ]


def sched_update_event(e):
    return [
        e["type"],
        e["typeDesc"],
        e.get("effectiveDate", ""),
        e["disclosuredDate"],
        e["content"],
        e["numberOfShares"]
    ]


def sched_issue_event(e):
    return [
        e["type"],
        e["typeDesc"],
        e["effectiveDate"],
        e["disclosuredDate"],
        e["expiredDate"],
        e["content"],
        e["numberOfShares"]
    ]

def kind_div_event(e):
    return [
        e["type"],
        e["typeDesc"],
        e["effectiveDate"],
        e["disclosuredDate"],
        e["expiredDate"],
        e["content"],
        e["ratio"]
    ]

def sched_div_event(e):
    return [
        e["type"],
        e["typeDesc"],
        e["disclosuredDate"],
        e["content"],
        e.get("ratio", ""),
        e.get("divYear", "")
    ]

def noticed_event(e):
    return [
        e["type"],
        e["typeDesc"],
        e["effectiveDate"],
        e["disclosuredDate"],
        e["content"]
    ]


def poll_event(e):
    return [
        e["type"],
        e["typeDesc"],
        e["effectiveDate"],
        e["disclosuredDate"],
        e.get("expiredDate", ""),
        e["content"],
        e.get("actualDate", "")
    ]


_convert_dict = {
    "dividend": dividend_event,
    "meeting": meeting_event,
    "schedupdate": sched_update_event,
    "schedissue": sched_issue_event,
    "kinddiv": kind_div_event,
    'scheddiv': sched_div_event,
    'noticed': noticed_event,
    'poll': poll_event
}

def get_company_events(symbol):
    url = f"https://finfo-api.vndirect.com.vn/events?symbols={symbol}"
    payload = {}
    headers = {}
    resp = requests.request("GET", url, headers=headers, data=payload)

    events = resp.json()["data"]

    df_dict = dict()

    for e in events:
        type_l =e["type"].lower()
        if type_l == "stockdiv":
            type_l = "dividend"

        if type_l not in df_dict:
            if type_l == "dividend":
                df_dict[type_l] = {
                    "type": type_l,
                    "df": pd.DataFrame(columns=[
                        'type', 'typeDesc', 'effectiveDate',
                        'disclosuredDate', 'expiredDate', 'content', 'dividend',
                        'ratio', 'actualDate', 'divPeriod', 'divYear', 'numberOfShares'])
                }
            elif type_l == "meeting":
                df_dict[type_l] = {
                    "type": type_l,
                    "df": pd.DataFrame(columns=[
                        "type", "typeDesc", "effectiveDate", "disclosuredDate", "content"
                    ])
                }
            elif type_l == "schedupdate":
                df_dict[type_l] = {
                    "type": "sched_update",
                    "df": pd.DataFrame(columns=[
                        "type", "typeDesc", "effectiveDate", "disclosuredDate", "content", "numberOfShares"
                    ])
                }
            elif type_l == "schedissue":
                df_dict[type_l] = {
                    "type": "sched_issue",
                    "df": pd.DataFrame(columns=[
                        "type", "typeDesc", "effectiveDate", "disclosuredDate", "expiredDate", "content", "numberOfShares"
                    ])
                }
            elif type_l == "kinddiv":
                df_dict[type_l] = {
                    "type": "kind_div",
                    "df": pd.DataFrame(columns=[
                        "type", "typeDesc", "effectiveDate", "disclosuredDate", "expiredDate", "content",
                        "ratio"
                    ])
                }
            elif type_l == "scheddiv":
                df_dict[type_l] = {
                    "type": "sched_div",
                    "df": pd.DataFrame(columns=[
                        "type", "typeDesc", "disclosuredDate", "content",
                        "ratio", "divYear"
                    ])
                }
            elif type_l == "noticed":
                df_dict[type_l] = {
                    "type": "noticed",
                    "df": pd.DataFrame(columns=[
                        "type", "typeDesc", "effectiveDate", "disclosuredDate",
                        "content"
                    ])
                }
            elif type_l == "poll":
                df_dict[type_l] = {
                    "type": "poll",
                    "df": pd.DataFrame(columns=[
                        "type", "typeDesc", "effectiveDate", "disclosuredDate",
                        "expiredDate", "content", "actualDate"
                    ])
                }

        z = df_dict.get(type_l)
        if z is not None:
            df = z["df"]
            df.loc[len(df)] = _convert_dict[type_l](e)

    for k, v in df_dict.items():
        v["df"].sort_values(by=["disclosuredDate"], inplace=True)
        v["df"].reset_index(inplace=True, drop=True)
    return df_dict


