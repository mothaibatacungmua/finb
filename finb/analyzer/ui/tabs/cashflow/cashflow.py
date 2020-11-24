import os
import datetime
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from finb.analyzer.ui.app import application
from dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output, State
import dash_table as dtb
from dash.exceptions import PreventUpdate

from finb.utils.datahub import read_cashflow_by_year_range
from finb.analyzer.ui.tabs.common import list_symbols, CACHING_PATH, create_symbol_filter_box_func

card_name = "cashflow"
title = "Cashflow Analysis"
content_components = [
  dbc.Tabs(id=f"{card_name}-tabs"),
  html.Div(id=f"{card_name}-tab-content", className="p-4")
]


def initialize():
  global view_mode, prev_symbols
  view_mode.clear()
  prev_symbols = []

render, filter_symbols_by_sector = create_symbol_filter_box_func(title, card_name, content_components,  initialize)

prev_symbols = []
view_mode = dict()


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
      if sat is not None:
        symbol = sat.split("_")[0]
        if symbol != removing_symbol:
          tab_content = [view_mode[symbol]]
      view_mode.pop(removing_symbol)
    if len(adding_symbol) == 1:
      adding_symbol = adding_symbol[0]
      tab_children.append(dbc.Tab(label="%s" % adding_symbol, tab_id=f"{adding_symbol}_{card_name}"))
      view_mode[adding_symbol] = draw_cashflow(adding_symbol)[0]
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


def draw_cashflow(symbol):
  raw_df = None
  index = list_symbols.index(symbol)
  current_year = datetime.datetime.now().year
  raw_cache_path = os.path.join(CACHING_PATH, symbol, "cashflow.csv")

  if not os.path.exists(os.path.join(CACHING_PATH, symbol)):
    os.makedirs(os.path.join(CACHING_PATH, symbol))

  if os.path.exists(raw_cache_path):
    raw_df = pd.read_csv(raw_cache_path)
    raw_df.set_index("fields", inplace=True)

  if raw_df is None:
    raw_df = read_cashflow_by_year_range(symbol, current_year - 5, current_year)

    raw_df.to_csv(raw_cache_path)

  quarter_cols = raw_df.columns.tolist()

  columns = [{"name": "fields", "id": "fields", "type": "text"}] + \
    [{"name": i, "id": i,
      'type': 'numeric',
      "format": Format(scheme=Scheme.fixed, group=',', precision=0)} for i in raw_df.columns]
  data = raw_df.to_dict("records")

  for f, r in zip(raw_df.index.tolist(), data):
    r["fields"] = f

  cashflow_table = html.Div([
    dtb.DataTable(
      id={
        'type': f'dynamic-{card_name}',
        'index': index
      },
      columns=columns,
      data=data,
      style_cell_conditional=[
        {'if': {'column_id': "fields"},
         'textAlign': 'left', 'maxWidth': '350px'},
        {'if': {'column_id': quarter_cols},
         'minWidth': '150px'}
      ],
      style_table={'overflowX': 'scroll', 'overflowY': 'scroll', 'height': '700px', 'minWidth': '100%'},
      style_header={
        'backgroundColor': 'rgb(230,230,230)',
        'fontWeight': 'bold'
      },
      style_cell={"marginLeft": "0px", 'whiteSpace': 'normal',
        'height': 'auto'},
      style_data_conditional=[
        {'if': {'row_index': [0, 25, 51, 53]}, 'fontWeight': 'bold'},
        {'if': {'row_index': [24, 37, 49, 50]}, 'fontWeight': 'bold', 'color': 'red'},
        {'if': {'row_index': [1, 2, 14, 38]},
         'fontWeight': 'bold', 'color': 'blue'},
        {'if': {'column_id': 'fields', 'row_index': [1, 2, 14, 38]},
         'backgroundColor': 'rgb(230,230,230)'}],
      fixed_columns={'headers': True, 'data': 1},
      fixed_rows={'headers': True, 'data': 0},
      css=[{'selector': '.row', 'rule': 'margin: 0;flex-wrap: nowrap'}],

    ),
    html.Div(children="", style={'paddingBottom': '50px'}),
  ])

  return cashflow_table, columns, data
