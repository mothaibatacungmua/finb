import os
import pandas as pd
import datetime
from finb.utils.datahub import \
  read_considered_df, read_balance_sheet_with_year_range, read_income_statement_with_year_range
from finb.utils.visualize import generate_colors_pool
from finb import PROJECT_PATH


companies_df = read_considered_df().copy().sort_index()
list_symbols = companies_df.index.tolist()
company_names = companies_df["companyName"].tolist()

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

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from finb.analyzer.ui.app import application

def create_symbol_filter_box_func(title, card_name, content_components, initialize_func=None):
  def render():
    if initialize_func is not None:
      initialize_func()
    content = dbc.Container([
      dbc.Row(html.H5([title])),
      dbc.Row([
        dcc.Dropdown(
          id=f'{card_name}-sectors',
          options=[{'label': s, 'value': s}
                   for s in industries],
          value="Tất cả",
          style={"width": "100%"}
        )
      ]),
      dbc.Row([
        dcc.Dropdown(
          id=f'{card_name}-symbols',
          options=[{'label': f"{s}-{n}", 'value': n}
                   for s, n in zip(list_symbols, company_names)],
          value=[],
          multi=True,
          style={"width": "100%"},
          clearable=False
        )
      ]),
      *content_components
    ], style={"max-width": "1600px"})

    return content

  @application.callback(
    Output(f"{card_name}-symbols", "options"),
    [Input(f"{card_name}-sectors", "value")]
  )
  def filter_symbols_by_sector(sector):
    if sector is None:
      raise PreventUpdate

    if sector == "Tất cả":
      return [{'label': f"{s}-{n}", 'value': s} for s, n in zip(list_symbols, company_names)]
    df = companies_df[companies_df["industryName"] == sector].sort_index()

    x = df.index.tolist()
    name = df["companyName"].tolist()
    return [{'label': f"{s}-{n}", 'value': n} for s, n in zip(x, name)]

  return render, filter_symbols_by_sector