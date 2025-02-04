# -*- coding: utf-8 -*-
"""PMCC 2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hIuNPnMzlmJjulxZexuNy_mLLtahRLyJ
"""

from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Parameters
num_samples = 100
sample_size = 10
num_iterations = 50000
adjusted_mean = 25.5
adjusted_std_dev = (50 - 1) / 6

# Generate data
np.random.seed(42)
data_main = np.random.normal(adjusted_mean, adjusted_std_dev, (num_samples, 2))
data_main = np.clip(data_main, 1, 50)
df_main = pd.DataFrame(data_main, columns=['Value 1', 'Value 2'])

def compute_pmcc(sample_size, threshold):
    pmcc_values = [
        np.corrcoef(df_main.sample(n=sample_size, replace=True)['Value 1'],
                    df_main.sample(n=sample_size, replace=True)['Value 2'])[0, 1]
        for _ in range(num_iterations)
    ]

    pmcc_values = np.array(pmcc_values)
    within_threshold = np.sum(np.abs(pmcc_values) <= threshold) / num_iterations
    outside_threshold = np.sum(np.abs(pmcc_values) > threshold) / num_iterations
    return pmcc_values, within_threshold, outside_threshold

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("PMCC Analysis Dashboard", className='text-center mt-4 mb-4'),

    dbc.Row([
        dbc.Col([
            html.Label("Select Sample Size:"),
            dcc.Dropdown(
                id='sample-size',
                options=[{'label': i, 'value': i} for i in range(5, 21)],
                value=10,
                clearable=False
            ),
        ], width=4),

        dbc.Col([
            html.Label("Set Threshold:"),
            dcc.Slider(
                id='threshold',
                min=0.4, max=0.8, step=0.01,
                value=0.6319,
                marks={i: str(i) for i in np.arange(0.4, 0.81, 0.1)}
            )
        ], width=8)
    ]),

    html.Br(),
    html.Div(id='stats-output', className='text-center'),

    dcc.Graph(id='histogram'),

    html.Hr(),
    html.H4("Generated Dataset (First 10 Rows):", className='mt-4'),
    dash_table.DataTable(
        id='data-table',
        columns=[{"name": i, "id": i} for i in df_main.columns],
        data=df_main.head(10).to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'}
    )
])

@app.callback(
    [Output('histogram', 'figure'), Output('stats-output', 'children')],
    [Input('sample-size', 'value'), Input('threshold', 'value')]
)
def update_graph(sample_size, threshold):
    pmcc_values, within_threshold, outside_threshold = compute_pmcc(sample_size, threshold)

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=pmcc_values, nbinsx=50, name='PMCC Values', marker_color='blue', opacity=0.7))
    fig.add_vline(x=-threshold, line_dash="dash", line_color="red", annotation_text=f"-{threshold}")
    fig.add_vline(x=threshold, line_dash="dash", line_color="red", annotation_text=f"{threshold}")
    fig.update_layout(
        title="Distribution of PMCC Values (50,000 Iterations)",
        xaxis_title="PMCC Values",
        yaxis_title="Density",
        template="plotly_white"
    )

    stats_text = (
        f"Proportion of PMCC values within ±{threshold}: {within_threshold:.4f}<br>"
        f"Proportion of PMCC values outside ±{threshold}: {outside_threshold:.4f}"
    )

    return fig, stats_text

if __name__ == '__main__':
    app.run_server(debug=True)

