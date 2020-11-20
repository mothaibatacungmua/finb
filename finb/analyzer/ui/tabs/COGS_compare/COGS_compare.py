import pandas as pd
import random
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from finb.analyzer.ui.app import application
from dash.dependencies import Input, Output, MATCH, State
from dash.exceptions import PreventUpdate

from finb.analyzer.ui.tabs.common import \
  companies_df, list_symbols, industries, read_income_statement_with_cache, colors_pool
from finb.utils.visualize import generate_comparing_chart

card_name = "cogs-compare"
def render():
  global draw_percent_df, draw_raw_df, prev_symbols
  draw_percent_df = None
  draw_raw_df = None
  prev_symbols = []
  content = dbc.Container([
    dbc.Row(html.H5(["COGS Compare"])),
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
        style = {"width": "100%"}
      )
    ]),
    dbc.Row([
      html.Div(id=f"{card_name}-chart-raw", className="w-50 p-3"),
      html.Div(id=f"{card_name}-chart-percent", className="w-50 p-3"),
    ])
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
    return [{'label': s, 'value': s} for s in list_symbols]
  df = companies_df[companies_df["industryName"] == sector]

  x = df.index.tolist()
  x.sort()
  return [{'label': s, 'value': s} for s in x]


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
    return [dcc.Graph(figure=generate_comparing_chart(draw_raw_df, title="COGS Raw"))], \
           [dcc.Graph(figure=generate_comparing_chart(draw_percent_df, title="COGS over Revenue Percent"))]

  elif len(adding_symbol) == 1:
    adding_symbol = adding_symbol[0]
    raw_df, percent_df = read_income_statement_with_cache(adding_symbol)

    if draw_raw_df is None:
      draw_raw_df = pd.DataFrame(columns=raw_df.columns.tolist() + ["color"])
    if draw_percent_df is None:
      draw_percent_df = pd.DataFrame(columns=percent_df.columns.tolist() + ["color"])

    raw_s = raw_df.loc["4. Giá vốn hàng bán"]
    raw_s.name = adding_symbol
    draw_raw_df = draw_raw_df.append(raw_s)

    persent_s = percent_df.loc["4. Giá vốn hàng bán"]
    persent_s.name = adding_symbol
    draw_percent_df = draw_percent_df.append(persent_s)

    displayed_colors = set(draw_raw_df['color'].values.tolist())
    available_colors = list(set(colors_pool).difference(displayed_colors))

    rc = random.choice(available_colors)
    draw_raw_df.loc[adding_symbol, 'color'] = rc
    draw_percent_df.loc[adding_symbol, 'color'] = rc
    prev_symbols = symbols
    return [dcc.Graph(figure=generate_comparing_chart(draw_raw_df, title="COGS Raw"))], \
           [dcc.Graph(figure=generate_comparing_chart(draw_percent_df, title="COGS over Revenue Percent"))]

  raise PreventUpdate