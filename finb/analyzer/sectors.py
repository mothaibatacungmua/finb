# https://github.com/plotly/dash-stock-tickers-demo-app/blob/master/app.py
# https://github.com/facultyai/dash-bootstrap-components/blob/master/examples/advanced-component-usage/graphs_in_tabs.py
# https://stackoverflow.com/questions/50213761/changing-visibility-of-a-dash-component-by-updating-other-component
# https://community.plotly.com/t/expand-collapse-rows-of-datatable/29426
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dtb
from dash_table.Format import Format, Scheme
from dash.exceptions import PreventUpdate
import datetime
from dash.dependencies import Input, Output, MATCH, State
from finb.utils.visualize import generate_price_chart
from finb.utils.datahub import read_price_df, read_companies_df, get_same_industry, read_balance_sheet_with_year_range

sector_df = get_same_industry("CTD")
list_symbols = sorted(sector_df.index.tolist())
current_year = datetime.datetime.now().year
start_date = "%d-01-01" % (current_year - 5)
children = []
companies_df = read_companies_df(True)



external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = dbc.Container([
    html.Div([
        dbc.Tabs(
            [
                dbc.Tab(label="Technical", tab_id="technical"),
                dbc.Tab(label="Fundamental", tab_id="fundamental"),
            ],
            id="tabs",
            active_tab="technical",
        ),
        dcc.Dropdown(
            id='symbol-input',
            options=[{'label': s, 'value': s}
                     for s in list_symbols],
            value=[],
            multi=True
        ),
        html.Div(id="tab-content", className="p-4"),
    ]),
], style={'max-width': 1600})


prev_tickers = set()

@app.callback(
    Output("tab-content", "children"),
    [Input("symbol-input", "value"),
    Input("tabs", "active_tab")],
    [State("tab-content", "children")]
)
def render_tab_content(tickers, active_tab, current_children):
    global prev_tickers

    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    content = current_children
    if button_id == "tabs":
        prev_tickers = set()
        content = []
    if button_id == "symbol-input" or button_id == "tabs":
        if content is None:
            content = []
        if active_tab == "technical":
            content.extend(draw_technical_graph(tickers))
            # update prev_tickers
            prev_tickers = set(tickers)
        elif active_tab == "fundamental":
            content.extend(draw_balance_sheet(tickers))
            prev_tickers = set(tickers)

    return content


technical_graph_cache = dict()

def draw_technical_graph(tickers):
    global technical_graph_cache, prev_tickers
    graphs = []

    for i, symbol in enumerate(sorted(tickers)):
        if symbol in prev_tickers:
            continue
        price_df = read_price_df(symbol)
        price_df = price_df.loc[start_date:]

        company_info = companies_df.loc[symbol]
        if symbol not in technical_graph_cache:
            technical_graph_cache[symbol] = \
                html.Div(children=[
                    html.H3(children=company_info.companyName + f" ({company_info.floor}:{symbol})", style={'textAlign': 'center'}),
                    html.H4(children="Price", style={'textAlign': 'center'}),
                    dcc.Graph(
                        id=symbol + "-price-graph",
                        figure=generate_price_chart(price_df, show_volume=True),
                        style={"max-height": 900}
                    )
                ])
        graphs.append(technical_graph_cache[symbol])
    return graphs


balace_sheet_cache = dict()

def draw_balance_sheet(tickers):
    global balace_sheet_cache
    graphs = []

    for i, symbol in enumerate(sorted(tickers)):
        if symbol in prev_tickers:
            continue
        if symbol not in balace_sheet_cache:
            raw_df, percent_df = read_balance_sheet_with_year_range(symbol, current_year-5, current_year, "both")
            balace_sheet_cache[symbol] = (raw_df, percent_df)
        else:
            raw_df, percent_df = balace_sheet_cache[symbol]

        # print(raw_df.to_dict("records"))

        data = raw_df.to_dict("records")
        quarter_cols = raw_df.columns.tolist()
        company_info = companies_df.loc[symbol]

        for f, r in zip(raw_df.index.tolist(), data):
            r["fields"] = f

        raw_balance_sheet_table = html.Div([
            dbc.Row(html.H4(company_info.companyName + f" ({company_info.floor}:{symbol})", style={'textAlign': 'left', 'paddingBottom': "20px"})),
            dbc.Row(html.H5("Bảng Cân Đối Kế Toán", style={'textAlign': 'left', 'paddingLeft':'15px'})),
            dbc.DropdownMenu([
                dbc.DropdownMenuItem("Raw", id={'type': 'dynamic-view-raw', 'index': i}),
                dbc.DropdownMenuItem("Percent", id={'type': 'dynamic-view-percent', 'index': i})
            ], label="View"),
            dtb.DataTable(
                id={
                    'type': 'dynamic-balance-sheet',
                    'index': i
                },
                columns=[{"name": "fields", "id": "fields", "type":"text"}] +
                        [{"name":i, "id":i,
                          'type': 'numeric',
                          "format": Format(scheme=Scheme.fixed, group=',', precision=0)} for i in raw_df.columns],
                data=data,
                style_cell_conditional=[
                    {'if': {'column_id': "fields"},
                        'textAlign': 'left'},
                    {'if': {'column_id': quarter_cols},
                     'minWidth':'150px'}
                ],
                style_table={'overflowX': 'scroll', 'overflowY': 'scroll', 'height':'400px', 'minWidth': '100%'},
                style_header={
                    'backgroundColor': 'rgb(230,230,230)',
                    'fontWeight': 'bold'
                },
                style_cell={"marginLeft":"0px"},
                style_data_conditional=[
                    {'if':{'row_index':[1, 26, 55, 57, 87, 109]}, 'fontWeight': 'bold'},
                    {'if': {'row_index': [0, 56]}, 'fontWeight': 'bold', 'color':'red'},
                    {'if': {'row_index': [2, 5, 9, 17, 20, 27, 34, 40, 41, 44, 50, 54, 58, 74, 88, 105]},
                            'fontWeight': 'bold', 'color':'blue'},
                    {'if': {'column_id':'fields', 'row_index': [2, 5, 9, 17, 20, 27, 34, 40, 41, 44, 50, 54, 58, 74, 88, 105]},
                     'backgroundColor': 'rgb(230,230,230)'}],
                fixed_columns={'headers': True, 'data':1},
                fixed_rows={'headers': True, 'data':0},
                css=[{'selector': '.row', 'rule': 'margin: 0;flex-wrap: nowrap'}],

            ),
            html.Div(children="", style={'paddingBottom': '50px'}),
        ])
        graphs.append(raw_balance_sheet_table)

    return graphs

@app.callback(
    [Output({'type': 'dynamic-balance-sheet', 'index': MATCH}, 'columns'), Output({'type': 'dynamic-balance-sheet', 'index': MATCH}, 'data')],
    [Input({'type': 'dynamic-view-percent', 'index':MATCH}, 'n_clicks')],
    [State({'type': 'dynamic-view-percent', 'index':MATCH}, 'id'),
     State("symbol-input", "value")]
)
def view_percent_balance_sheet(n_clicks, id, tickers):
    if n_clicks is not None:
        raw_df, percent_df = balace_sheet_cache[tickers[id['index']]]

        columns = [{"name": "fields", "id": "fields", "type": "text"}] + \
                [{"name": i, "id": i,
                  'type': 'numeric',
                  "format": Format(scheme=Scheme.percentage, precision=2)} for i in percent_df.columns]
        data = percent_df.to_dict("records")
        for f, r in zip(percent_df.index.tolist(), data):
            r["fields"] = f

        return columns, data
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)