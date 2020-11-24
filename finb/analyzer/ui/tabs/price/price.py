import datetime
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from finb.analyzer.ui.tabs.common import companies_df, create_symbol_filter_box_func
from finb.analyzer.ui.app import application
from finb.utils.visualize import generate_price_chart
from finb.utils.datahub import read_price_df


card_name = "price-history"
title = "Price History"
content_components = [
  dbc.Tabs(id=f"{card_name}-tabs"),
  html.Div(id=f"{card_name}-tab-content", className="p-4")
]

def initialize():
  global view_mode, prev_symbols
  view_mode.clear()
  prev_symbols = []

render, filter_symbols_by_sector = create_symbol_filter_box_func(title, card_name, content_components, initialize)

view_mode = dict()
prev_symbols = []

@application.callback(
    [Output(f"{card_name}-tabs", "children"),
     Output(f"{card_name}-tab-content", "children")],
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
      view_mode[adding_symbol] = draw_price_history(adding_symbol)
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


def draw_price_history(symbol):
  current_year = datetime.datetime.now().year
  start_date = "%d-01-01" % (current_year - 5)
  price_df = read_price_df(symbol)
  price_df = price_df.loc[start_date:]
  company_info = companies_df.loc[symbol]

  return html.Div(children=[
                    html.H3(children=company_info.companyName + f" ({company_info.floor}:{symbol})", style={'textAlign': 'center'}),
                    dcc.Graph(
                        id=symbol + "-price-graph",
                        figure=generate_price_chart(price_df, show_volume=True),
                        style={"max-height": 900}
                    )
                ])