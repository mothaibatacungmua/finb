import os
import datetime
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from finb.analyzer.ui.app import application
from dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output, MATCH, State
import dash_table as dtb
from dash.exceptions import PreventUpdate

from finb.analyzer.ui.tabs.common import \
  companies_df, list_symbols, industries, read_income_statement_with_cache

card_name = "income-statement"
def render():
  global prev_symbols, view_mode
  view_mode.clear()
  prev_symbols = []

  content = dbc.Container([
    dbc.Row(html.H5(["Income Statement Analysis"])),
    dbc.Row([
      dcc.Dropdown(
        id=f'{card_name}-sectors',
        options=[{'label': s, 'value': s}
                 for s in industries],
        value="Tất cả",
        style = {"width": "100%"}
      )
    ]),
    dbc.Row([
      dcc.Dropdown(
        id=f'{card_name}-symbols',
        options=[{'label': s, 'value': s}
                 for s in list_symbols],
        value=[],
        multi=True,
        style = {"width": "100%"},
        clearable=False
      )
    ]),
    dbc.Tabs(id=f"{card_name}-tabs"),
    html.Div(id=f"{card_name}-tab-content", className="p-4"),
  ], style={"max-width": "1600px"})


  return content


prev_symbols = []
view_mode = dict()

@application.callback(
    Output(f"{card_name}-symbols", "options"),
    [Input(f"{card_name}-sectors", "value")]
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
      view_mode[adding_symbol] = draw_income_statement(adding_symbol, "raw")[0]
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


def draw_income_statement(symbol, format="raw"):
  index = list_symbols.index(symbol)
  raw_df, percent_df = read_income_statement_with_cache(symbol)

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
  income_statement_table = html.Div([
    dbc.DropdownMenu([
      dbc.DropdownMenuItem("Raw", id={'type': f'dynamic-{card_name}-view-raw', 'index': index}),
      dbc.DropdownMenuItem("Percent", id={'type': f'dynamic-{card_name}-view-percent', 'index': index})
    ], label="View"),
    dtb.DataTable(
      id={
        'type': f'dynamic-{card_name}',
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
        {'if': {'row_index': [0, 21]}, 'fontWeight': 'bold'}],
      fixed_columns={'headers': True, 'data': 1},
      fixed_rows={'headers': True, 'data': 0},
      css=[{'selector': '.row', 'rule': 'margin: 0;flex-wrap: nowrap'}],

    ),
    html.Div(children="", style={'paddingBottom': '50px'}),
  ])

  return income_statement_table, columns, data


@application.callback(
    [Output({'type': f'dynamic-{card_name}', 'index': MATCH}, 'columns'),
     Output({'type': f'dynamic-{card_name}', 'index': MATCH}, 'data')],
    [Input({'type': f'dynamic-{card_name}-view-raw', 'index':MATCH}, 'n_clicks'),
     Input({'type': f'dynamic-{card_name}-view-percent', 'index':MATCH}, 'n_clicks')],
     State(f"{card_name}-tabs", "active_tab")
)
def view_mode_income_statement(raw_click, percent_click, at):
  global view_mode
  if at is not None:
    symbol = at.split("_")[0]
    if raw_click is not None:
      table, columns, data = draw_income_statement(symbol, "raw")
      view_mode[symbol] = table
      return columns, data
    if percent_click is not None:
      table, columns, data = draw_income_statement(symbol, "percent")
      view_mode[symbol] = table
      return columns, data

  raise PreventUpdate