import pandas as pd
import random
import dash_core_components as dcc
from finb.analyzer.ui.app import application
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_html_components as html

from finb.analyzer.ui.tabs.common import \
  read_income_statement_with_cache, colors_pool, \
  create_symbol_filter_box_func
from finb.utils.visualize import generate_comparing_chart

card_name = "sga-compare"
title = "SG&A Compare"
content_components = [
  dbc.Row([
        html.Div(id=f"{card_name}-chart-raw", className="w-50 p-3"),
        html.Div(id=f"{card_name}-chart-percent", className="w-50 p-3"),
      ])
]

def initialize():
  global draw_raw_df, draw_percent_df, prev_symbols
  draw_raw_df = None
  draw_percent_df = None
  prev_symbols = []

render, filter_symbols_by_sector = create_symbol_filter_box_func(title, card_name, content_components, initialize)

draw_raw_df = None
draw_percent_df = None
prev_symbols = []

@application.callback(
    [Output(f"{card_name}-chart-raw", "children"),
     Output(f"{card_name}-chart-percent", "children")],
    Input(f'{card_name}-symbols', "value")
)
def draw_cogs_chart_by_symbols(symbols):
  global draw_raw_df, draw_percent_df, prev_symbols

  input_symbols = set(symbols)
  z = set(prev_symbols)
  removing_symbol = list(z.difference(input_symbols))
  adding_symbol = list(input_symbols.difference(z))

  if len(removing_symbol) == 1:
    removing_symbol =  removing_symbol[0]
    if draw_raw_df is not None:
      draw_raw_df = draw_raw_df.drop(removing_symbol)
    if draw_percent_df is not None:
      draw_percent_df = draw_percent_df.drop(removing_symbol)
    prev_symbols = symbols
    return [dcc.Graph(figure=generate_comparing_chart(draw_raw_df, title="SG&A Raw"))], \
           [dcc.Graph(figure=generate_comparing_chart(draw_percent_df, title="SG&A over Revenue Percent"))]

  elif len(adding_symbol) == 1:
    adding_symbol = adding_symbol[0]
    raw_df, percent_df = read_income_statement_with_cache(adding_symbol)

    if draw_raw_df is None:
      draw_raw_df = pd.DataFrame(columns=raw_df.columns.tolist() + ["color"])
    if draw_percent_df is None:
      draw_percent_df = pd.DataFrame(columns=percent_df.columns.tolist() + ["color"])

    raw_s = raw_df.loc["9. Chi phí bán hàng"] + raw_df.loc["10. Chi phí quản lý doanh nghiệp"]
    raw_s.name = adding_symbol
    draw_raw_df = draw_raw_df.append(raw_s)

    persent_s = percent_df.loc["9. Chi phí bán hàng"] + percent_df.loc["10. Chi phí quản lý doanh nghiệp"]
    persent_s.name = adding_symbol
    draw_percent_df = draw_percent_df.append(persent_s)

    displayed_colors = set(draw_raw_df['color'].values.tolist())
    available_colors = list(set(colors_pool).difference(displayed_colors))

    rc = random.choice(available_colors)
    draw_raw_df.loc[adding_symbol, 'color'] = rc
    draw_percent_df.loc[adding_symbol, 'color'] = rc
    prev_symbols = symbols
    return [dcc.Graph(figure=generate_comparing_chart(draw_raw_df, title="SG&A Raw"))], \
           [dcc.Graph(figure=generate_comparing_chart(draw_percent_df, title="SG&A over Revenue Percent"))]

  raise PreventUpdate