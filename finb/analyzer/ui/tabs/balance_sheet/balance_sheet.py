import os
import datetime
import pandas as pd
import dash
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
  global prev_symbols, view_mode
  view_mode.clear()
  prev_symbols = []

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


prev_symbols = []
view_mode = dict()

@application.callback(
    Output("balance-sheet-symbols", "options"),
    [Input("balance-sheet-sectors", "value")]
)
def filter_symbols_by_sector(sector):
  if sector is None:
    raise PreventUpdate

  if sector == "Tất cả":
    return [{'label': s, 'value': s} for s in list_symbols]
  df = companies_df[companies_df["industryName"] == sector]

  x = df.index.tolist()
  x.sort()
  return [{'label': s, 'value': s} for s in x]


@application.callback(
    [Output("balance-sheet-tabs", "children"),
     Output("balance-sheet-tab-content", "children")],
    [Input("balance-sheet-symbols", "value"),
     Input("balance-sheet-tabs", "active_tab")],
    State("balance-sheet-tabs", "children")
)
def render_by_symbol(symbols, iat, children):
  global prev_symbols
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

  if button_id == "balance-sheet-symbols":
    input_symbols = set(symbols)
    z = set(prev_symbols)
    removing_symbol = list(z.difference(input_symbols))
    adding_symbol = list(input_symbols.difference(z))


    if len(removing_symbol) == 1:
      removing_symbol = removing_symbol[0]
      removing_index = prev_symbols.index(removing_symbol)
      tab_children.pop(removing_index)
      view_mode.pop(removing_symbol)
    if len(adding_symbol) == 1:
      adding_symbol = adding_symbol[0]
      tab_children.append(dbc.Tab(label="%s" % adding_symbol, tab_id="%s_balance-sheet" % adding_symbol))
      view_mode[adding_symbol] = draw_balance_sheet(adding_symbol, "raw")[0]
    prev_symbols = symbols

    return tab_children, tab_content
  elif button_id == "balance-sheet-tabs":
    symbol = iat.split("_")[0]
    return tab_children, view_mode[symbol]
  raise PreventUpdate


def draw_balance_sheet(symbol, format="raw"):
  raw_df = None
  percent_df = None
  index = list_symbols.index(symbol)
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

  quarter_cols = raw_df.columns.tolist()

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

  return balance_sheet_table, columns, data

@application.callback(
    [Output({'type': 'dynamic-balance-sheet', 'index': MATCH}, 'columns'),
     Output({'type': 'dynamic-balance-sheet', 'index': MATCH}, 'data')],
    [Input({'type': 'dynamic-balance-sheet-view-raw', 'index':MATCH}, 'n_clicks'),
     Input({'type': 'dynamic-balance-sheet-view-percent', 'index':MATCH}, 'n_clicks')],
     State("balance-sheet-tabs", "active_tab")
)
def view_mode_balance_sheet(raw_click, percent_click, at):
  global view_mode
  if at is not None:
    symbol = at.split("_")[0]
    if raw_click is not None:
      table, columns, data = draw_balance_sheet(symbol, "raw")
      view_mode[symbol] = table
      return columns, data
    if percent_click is not None:
      table, columns, data = draw_balance_sheet(symbol, "percent")
      view_mode[symbol] = table
      return columns, data

  raise PreventUpdate
