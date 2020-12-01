import pandas as pd
import datetime
import dash
from finb.analyzer.ui.app import application
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_html_components as html
from collections import namedtuple
from finb.analyzer.ui.tabs.common import \
  create_symbol_filter_box_func, companies_df

from finb.utils.datahub import read_price_df, generate_weekly_quotes
from finb.utils.visualize import generate_return_chart
from finb.analyzer.process import compute_returns, compute_beta

card_name = "weekly-returns"
title = "Weekly Returns"
content_components = [
  dbc.Tabs(id=f"{card_name}-tabs"),
  html.Div(id=f"{card_name}-bar"),
  # dbc.Row([html.Div(id=f"{card_name}-scatter", className="p-4")])
]

def initialize():
  global view_mode, prev_symbols
  view_mode.clear()
  prev_symbols = []

render, filter_symbols_by_sector = create_symbol_filter_box_func(
  title, card_name, content_components, initialize, include_vnindex=True, include_vn30=True)

view_mode = dict()
prev_symbols = []

@application.callback(
    [Output(f"{card_name}-tabs", "children"),
     Output(f"{card_name}-bar", "children")],
    [Input(f"{card_name}-symbols", "value"),
     Input(f"{card_name}-tabs", "active_tab")],
  [State(f"{card_name}-tabs", "children"),
   State(f"{card_name}-tabs", "active_tab")]
)
def render_by_symbol(symbols, iat, children, sat):
  global prev_symbols, view_mode
  ctx = dash.callback_context

  if not ctx.triggered:
    button_id = 'No clicks yet'
  else:
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

  tab_content = []
  if children is None:
    tab_children = []
  else:
    tab_children = children

  if button_id == f"{card_name}-symbols":
    input_symbols = set(symbols)
    z = set(prev_symbols)
    removing_symbol = list(z.difference(input_symbols))
    adding_symbol = list(input_symbols.difference(z))

    if len(removing_symbol) == 1:
      removing_symbol = removing_symbol[0]
      removing_index = prev_symbols.index(removing_symbol)
      tab_children.pop(removing_index)
      view_mode.pop(removing_symbol)
      if sat is not None:
        symbol = sat.split("_")[0]
        if symbol != removing_symbol:
          tab_content = [view_mode[symbol]]
    if len(adding_symbol) == 1:
      adding_symbol = adding_symbol[0]
      tab_children.append(dbc.Tab(label="%s" % adding_symbol, tab_id=f"{adding_symbol}_{card_name}"))
      view_mode[adding_symbol] = draw_weekly_returns(adding_symbol)
      if sat is not None:
        symbol = sat.split("_")[0]
        if symbol in view_mode:
          tab_content = [view_mode[symbol]]
    prev_symbols = symbols

    return tab_children, tab_content
  elif button_id == f"{card_name}-tabs":
    symbol = iat.split("_")[0]
    return tab_children, view_mode[symbol]
  raise PreventUpdate


CompanyInfo = namedtuple('CompanyInfo', ['companyName', 'floor'])

def draw_weekly_returns(symbol):
  if not symbol in {'VNINDEX', 'VN30'}:
    company_info = companies_df.loc[symbol]
  else:
    company_info = CompanyInfo(companyName=symbol, floor="HOSE")

  current_year = datetime.datetime.now().year
  start_date = "%d-01-01" % (current_year - 5)
  daily_price_df = read_price_df(symbol)
  daily_price_df = daily_price_df.loc[start_date:]
  weekly_price_df = generate_weekly_quotes(daily_price_df)

  returns_df = compute_returns(weekly_price_df)

  return html.Div(children=[
    html.H3(children=company_info.companyName + f" ({company_info.floor}:{symbol})", style={'textAlign': 'center', 'paddingTop': "20px"}),
    dcc.Graph(
      id=symbol + "-weekly-returns",
      figure=generate_return_chart(returns_df, symbol),
      style={"max-height": 1024}
    )
  ])