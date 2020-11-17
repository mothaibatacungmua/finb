import os
import datetime
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from finb.analyzer.ui.app import application
from dash_table.Format import Format, Scheme
from finb.utils.datahub import read_balance_sheet_with_year_range
from finb.analyzer.ui.tabs.common import companies_df, list_symbols, industries, CACHING_PATH
from dash.dependencies import Input, Output, MATCH, State
import dash_table as dtb
from dash.exceptions import PreventUpdate


def render():
  global balance_sheet_cache
  balance_sheet_cache.clear()

  content = dbc.Container([
    dbc.Row(html.H5(["Balance Sheet Analysis"])),
    dbc.Row([
      dcc.Dropdown(
        id='balance-sheet-sectors',
        options=[{'label': s, 'value': s}
                 for s in industries],
        value="Tất cả",
        style = {"width": "100%"}
      )
    ]),
    dbc.Row([
      dcc.Dropdown(
        id='balance-sheet-symbols',
        options=[{'label': s, 'value': s}
                 for s in list_symbols],
        value=[],
        multi=True,
        style = {"width": "100%"}
      )
    ]),
    dbc.Tabs(id="balance-sheet-tabs"),
    html.Div(id="balance-sheet-tab-content", className="p-4"),
  ], style={"max-width": "1600px"})


  return content


prev_tickers = []

@application.callback(
    Output("balance-sheet-tabs", "children"),
    [Input("balance-sheet-symbols", "value")],
    [State("balance-sheet-tabs", "children")]
)
def render_by_symbol(tickers, children):
  global prev_tickers
  input_tickers = set(tickers)
  z = set(prev_tickers)
  removing_tickers = z.difference(input_tickers)
  adding_tickers = input_tickers.difference(z)

  if children is None:
    tab_children = []
  else:
    tab_children = children

  removing_indices = []
  for az in removing_tickers:
    removing_indices.append(prev_tickers.index(az))
  removing_indices.sort(reverse=True)
  for rmi in removing_indices:
    tab_children.pop(rmi)

  adding_indices = []
  for az in adding_tickers:
    adding_indices.append(tickers.index(az))
  adding_indices.sort(reverse=True)

  for adi in adding_indices:
    ticker = tickers[adi]
    tab_children.append(dbc.Tab(label="%s"%ticker, tab_id="%s_balance-sheet" % ticker))

  prev_tickers = tickers
  return tab_children


@application.callback(Output("balance-sheet-tab-content", "children"), [Input("balance-sheet-tabs", "active_tab")])
def switch_tab(at):
  if at is None:
    raise PreventUpdate
  symbol = at.split("_")[0]
  return draw_balance_sheet(symbol)


balance_sheet_cache = dict()

def draw_balance_sheet(symbol, format="raw"):
  global balance_sheet_cache

  raw_df = None
  percent_df = None
  index = list_symbols.index(symbol)
  current_year = datetime.datetime.now().year
  raw_cache_path = os.path.join(CACHING_PATH, symbol, "raw_balance_sheet.csv")
  percent_cache_path = os.path.join(CACHING_PATH, symbol, "percent_balance_sheet.csv")

  if not symbol in balance_sheet_cache:
    if not os.path.exists(os.path.join(CACHING_PATH, symbol)):
      os.makedirs(os.path.join(CACHING_PATH, symbol))

    if os.path.exists(raw_cache_path):
      raw_df = pd.read_csv(raw_cache_path)
      raw_df.set_index("fields", inplace=True)
    if os.path.exists(percent_cache_path):
      percent_df = pd.read_csv(percent_cache_path)
      percent_df.set_index("fields", inplace=True)
  else:
    raw_df, percent_df = balance_sheet_cache[symbol]

  if raw_df is None or percent_df is None:
    raw_df, percent_df = read_balance_sheet_with_year_range(symbol, current_year - 5, current_year, "both")

    raw_df.to_csv(raw_cache_path)
    percent_df.to_csv(percent_cache_path)

  balance_sheet_cache[symbol] = (raw_df, percent_df)
  quarter_cols = raw_df.columns.tolist()
  company_info = companies_df.loc[symbol]

  if format == "raw":
    columns = [{"name": "fields", "id": "fields", "type": "text"}] + \
      [{"name": i, "id": i,
        'type': 'numeric',
        "format": Format(scheme=Scheme.fixed, group=',', precision=0)} for i in raw_df.columns]
    data = raw_df.to_dict("records")
  else:
    columns = [{"name": "fields", "id": "fields", "type": "text"}] + \
              [{"name": i, "id": i,
                'type': 'numeric',
                "format": Format(scheme=Scheme.percentage, precision=2)} for i in percent_df.columns]
    data = percent_df.to_dict("records")

  for f, r in zip(raw_df.index.tolist(), data):
    r["fields"] = f
  balance_sheet_table = html.Div([
    dbc.Row(html.H5("Bảng Cân Đối Kế Toán", style={'textAlign': 'left', 'paddingLeft': '15px'})),
    dbc.DropdownMenu([
      dbc.DropdownMenuItem("Raw", id={'type': 'dynamic-balance-sheet-view-raw', 'index': index}),
      dbc.DropdownMenuItem("Percent", id={'type': 'dynamic-balance-sheet-view-percent', 'index': index})
    ], label="View"),
    dtb.DataTable(
      id={
        'type': 'dynamic-balance-sheet',
        'index': index
      },
      columns=columns,
      data=data,
      style_cell_conditional=[
        {'if': {'column_id': "fields"},
         'textAlign': 'left'},
        {'if': {'column_id': quarter_cols},
         'minWidth': '150px'}
      ],
      style_table={'overflowX': 'scroll', 'overflowY': 'scroll', 'height': '600px', 'minWidth': '100%'},
      style_header={
        'backgroundColor': 'rgb(230,230,230)',
        'fontWeight': 'bold'
      },
      style_cell={"marginLeft": "0px"},
      style_data_conditional=[
        {'if': {'row_index': [1, 26, 55, 57, 87, 109]}, 'fontWeight': 'bold'},
        {'if': {'row_index': [0, 56]}, 'fontWeight': 'bold', 'color': 'red'},
        {'if': {'row_index': [2, 5, 9, 17, 20, 27, 34, 40, 41, 44, 50, 54, 58, 74, 88, 105]},
         'fontWeight': 'bold', 'color': 'blue'},
        {'if': {'column_id': 'fields', 'row_index': [2, 5, 9, 17, 20, 27, 34, 40, 41, 44, 50, 54, 58, 74, 88, 105]},
         'backgroundColor': 'rgb(230,230,230)'}],
      fixed_columns={'headers': True, 'data': 1},
      fixed_rows={'headers': True, 'data': 0},
      css=[{'selector': '.row', 'rule': 'margin: 0;flex-wrap: nowrap'}],

    ),
    html.Div(children="", style={'paddingBottom': '50px'}),
  ])

  return balance_sheet_table


@application.callback(
    [Output({'type': 'dynamic-balance-sheet', 'index': MATCH}, 'columns'), Output({'type': 'dynamic-balance-sheet', 'index': MATCH}, 'data')],
    [Input({'type': 'dynamic-balance-sheet-view-raw', 'index':MATCH}, 'n_clicks'),
     Input({'type': 'dynamic-balance-sheet-view-percent', 'index':MATCH}, 'n_clicks')],
     State("balance-sheet-tabs", "active_tab")
)
def view_mode_balance_sheet(raw_click, percent_click, at):
  if at is not None:
    symbol = at.split("_")[0]
    if raw_click is not None:
      raw_df, percent_df = balance_sheet_cache[symbol]

      columns = [{"name": "fields", "id": "fields", "type": "text"}] + \
                [{"name": i, "id": i,
                  'type': 'numeric',
                  "format": Format(scheme=Scheme.fixed, group=',', precision=0)} for i in raw_df.columns]
      data = raw_df.to_dict("records")
      for f, r in zip(percent_df.index.tolist(), data):
          r["fields"] = f
      return columns, data
    if percent_click is not None:
      raw_df, percent_df = balance_sheet_cache[symbol]

      columns = [{"name": "fields", "id": "fields", "type": "text"}] + \
                [{"name": i, "id": i,
                  'type': 'numeric',
                  "format": Format(scheme=Scheme.percentage, precision=2)} for i in percent_df.columns]
      data = percent_df.to_dict("records")
      for f, r in zip(percent_df.index.tolist(), data):
        r["fields"] = f
      return columns, data

  raise PreventUpdate