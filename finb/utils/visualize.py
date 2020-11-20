# https://plotly.com/python/text-and-annotations/
# https://plotly.com/python/line-and-scatter/
# https://chart-studio.plotly.com/~jackp/17421/plotly-candlestick-chart-in-python/#/
# https://chart-studio.plotly.com/~empet/15608/relayout-method-to-change-the-layout-att/#/
# https://community.plotly.com/t/whats-the-correct-way-to-set-layout-properties-for-each-subplot/33000/3
# https://community.plotly.com/t/y-axis-autoscaling-with-x-range-sliders/10245/4
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib


INCREASING_COLOR = 'green'
DECREASING_COLOR = 'red'


def generate_price_chart(df, type="candlestick", show_volume=True):
    row = 1
    specs = [[{"type": "candlestick", "rowspan": 3}],[{}],[{}]]

    colors = []
    for i in range(len(df.index)):
        if i != 0:
            if df.Close[i] > df.Close[i - 1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)

    if show_volume:
        specs.append([{"type": "bar"}])
        row = 4
    fig = make_subplots(
        rows=row, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        specs=specs
    )

    if type == "candlestick":
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df.Open,
                high=df.High,
                low=df.Low,
                close=df.Close,
            ), row=1, col=1
        )
    elif type == "line":
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df.Close
            ), row=1, col=1
        )

    layout = go.Layout(
        xaxis=dict(rangeslider=dict(visible=False), showgrid=True),
        yaxis=dict(title="Price", showgrid=True, color="black", autorange=True, fixedrange=False),
        showlegend=False,
        height=900
    )


    if show_volume:
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df.Volume,
                yaxis="y",
                marker=dict(color=colors),
                name='Volume'),
            row=row, col=1
        )

    fig.update_layout(layout)

    return fig


# https://stackoverflow.com/questions/55138359/plotly-stacked-bar-chart-pandas-dataframe
# https://stackoverflow.com/questions/44044754/how-to-change-bar-size-plotly-time-series
# https://plotly.com/python/bar-charts/#customizing-individual-bar-colors
# https://blog.quantinsti.com/gold-price-prediction-using-machine-learning-python/

def generate_return_chart(df_returns, symbol=None):
    x = df_returns.index
    y = df_returns["Return"].values
    colors = []
    for v in y:
        if v <= 0:
            colors.append(DECREASING_COLOR)
        else:
            colors.append(INCREASING_COLOR)

    fig = go.Figure(data=[go.Bar(
        x=x,
        y=y,
        marker_color=colors  # marker color can be a single color value or an iterable
    )])
    if symbol is not None:
        fig.update_layout(title_text=f'{symbol} Returns')
    return fig


def generate_colors_pool():
    hex_colors_only = []
    for name, hex in matplotlib.colors.cnames.items():
        hex_colors_only.append(hex)

    return hex_colors_only


def generate_comparing_chart(df: pd.DataFrame, title=None):
    """

    :param df: include columns as x, index as symbols, data as y
    :return: go.Figure
    """

    symbols = df.index.tolist()
    x = df.columns[:-1]

    fig = go.Figure()
    for symbol in symbols:
        fig.add_trace(go.Scatter(
            x=x,
            y=df.loc[symbol].values[:-1],
            mode='lines+markers',
            line=dict(color=df.loc[symbol]['color']),
            name=symbol
        ))
    fig.update_layout(title=title, title_x=0.5)
    return fig