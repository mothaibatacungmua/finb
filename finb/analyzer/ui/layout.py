import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from finb.analyzer.ui.tabs import TABS_DICT
from finb.analyzer.ui.app import application


def generate_layout():
  global  prev_analyzers
  prev_analyzers = []
  layout = dbc.Container([
    html.Div([
      dcc.Dropdown(
        id='analyzer-panel',
        options=[
          {'value': 'price_analyzer', 'label': 'Price'},
          {'value': 'balance_sheet_analyzer', 'label': 'Balance Sheet'},
          {'value': 'income_statement_analyzer', 'label': 'Income Statement'},
          {'value': 'cashflow_analyzer', 'label': 'Cashflow'},
          {'value': 'cogs_compare_analyzer', 'label': 'COGS compare'},
          {'value': 'sga_compare_analyzer', 'label': 'SGA compare'},
          {'value': 'revenue_analyzer', 'label': 'Revenue'},
          {'value': 'net_income_analyzer', 'label': 'Net Income'}
        ],
        value=[],
        multi=True
      ),
    ]),
    html.Div(id="analyzer-content", className="p-4")
  ], style={'max-width': 1600})

  return layout



prev_analyzers = []

@application.callback(
    Output("analyzer-content", "children"),
    [Input("analyzer-panel", "value")],
    [State("analyzer-content", "children")]
)
def analyzer_content(analyzers, children):
  global prev_analyzers
  if analyzers is None:
    raise PreventUpdate

  input_analyzers = set(analyzers)
  z = set(prev_analyzers)
  removing_analyzers = z.difference(input_analyzers)
  adding_analyzers = input_analyzers.difference(z)

  if children is None:
    children = []

  removing_indices = []
  for az in removing_analyzers:
    removing_indices.append(prev_analyzers.index(az))
  removing_indices.sort(reverse=True)
  for rmi in removing_indices:
    if len(children) > rmi:
      children.pop(rmi)

  adding_indices = []
  for az in adding_analyzers:
    adding_indices.append(analyzers.index(az))
  adding_indices.sort(reverse=True)

  for adi in adding_indices:
    az = analyzers[adi]
    children.append(TABS_DICT[az]())

  prev_analyzers = analyzers
  return children

application.layout = generate_layout()