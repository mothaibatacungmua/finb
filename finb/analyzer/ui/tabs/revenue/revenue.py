import pandas as pd
import random
import dash_core_components as dcc
from finb.analyzer.ui.app import application
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_html_components as html

from finb.analyzer.ui.tabs.common import \
  read_income_statement_with_cache, colors_pool, create_symbol_filter_box_func
from finb.utils.visualize import generate_comparing_chart

card_name = "revenue"
title = "Revenue and Net Revenue"
content_components = [
  dbc.Row([
        html.Div(id=f"{card_name}-chart-gross", className="w-50 p-3"),
        html.Div(id=f"{card_name}-chart-net", className="w-50 p-3"),
      ])
]

def initialize():
  global draw_gross_df, draw_net_df, prev_symbols
  draw_gross_df = None
  draw_net_df = None
  prev_symbols = []

render, filter_symbols_by_sector = create_symbol_filter_box_func(title, card_name, content_components, initialize)

draw_gross_df = None
draw_net_df = None
prev_symbols = []

@application.callback(
    [Output(f"{card_name}-chart-gross", "children"),
     Output(f"{card_name}-chart-net", "children")],
    Input(f'{card_name}-symbols', "value")
)
def draw_revenue_chart_by_symbols(symbols):
  global draw_gross_df, draw_net_df, prev_symbols

  input_symbols = set(symbols)
  z = set(prev_symbols)
  removing_symbol = list(z.difference(input_symbols))
  adding_symbol = list(input_symbols.difference(z))

  if len(removing_symbol) == 1:
    removing_symbol =  removing_symbol[0]
    if draw_gross_df is not None:
      draw_gross_df = draw_gross_df.drop(removing_symbol)
    if draw_net_df is not None:
      draw_net_df = draw_net_df.drop(removing_symbol)
    prev_symbols = symbols
    return [dcc.Graph(figure=generate_comparing_chart(draw_gross_df, title="Gross Revenue"))], \
           [dcc.Graph(figure=generate_comparing_chart(draw_net_df, title="Net Revenue"))]

  elif len(adding_symbol) == 1:
    adding_symbol = adding_symbol[0]
    raw_df, percent_df = read_income_statement_with_cache(adding_symbol)

    if draw_gross_df is None:
      draw_gross_df = pd.DataFrame(columns=raw_df.columns.tolist() + ["color"])
    if draw_net_df is None:
      draw_net_df = pd.DataFrame(columns=percent_df.columns.tolist() + ["color"])

    gross_s = raw_df.loc["1. Tổng doanh thu hoạt động kinh doanh"]
    gross_s.name = adding_symbol
    draw_gross_df = draw_gross_df.append(gross_s)

    net_s = raw_df.loc["3. Doanh thu thuần (1)-(2)"]
    net_s.name = adding_symbol
    draw_net_df = draw_net_df.append(net_s)

    displayed_colors = set(draw_gross_df['color'].values.tolist())
    available_colors = list(set(colors_pool).difference(displayed_colors))

    rc = random.choice(available_colors)
    draw_gross_df.loc[adding_symbol, 'color'] = rc
    draw_net_df.loc[adding_symbol, 'color'] = rc
    prev_symbols = symbols
    return [dcc.Graph(figure=generate_comparing_chart(draw_gross_df, title="Gross Revenue"))], \
           [dcc.Graph(figure=generate_comparing_chart(draw_net_df, title="Net Revenue"))]

  raise PreventUpdate