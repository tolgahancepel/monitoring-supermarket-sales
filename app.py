# Importing libraries and reading the dataset

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)

df = pd.read_csv("ToyotaCorolla.csv")

# ------------------------------------------------------------------------------
# Creating Some Components

cat_features = ["FuelType", "HP", "MetColor", "Automatic", "CC", "Doors"]

controls1 = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Categorical Feature:"),
                dcc.Dropdown(
                    id="cat_variable",
                    options=[
                        {"label": "Fuel Type", "value": "FuelType"},
                        {"label": "HP", "value": "HP"},
                        {"label": "MetColor Type", "value": "MetColor"},
                        {"label": "Automatic", "value": "Automatic"},
                        {"label": "CC", "value": "CC"},
                        {"label": "Doors", "value": "Doors"},
                    ],
                    value="FuelType",
                    multi=False
                ),
            ]
        )
    ],
    body=True,
)

controls2 = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Numerical Feature:"),
                dcc.Dropdown(
                    id="num_variable",
                    options=[
                        {"label": "Age", "value": "Age"},
                        {"label": "KM", "value": "KM"}
                    ],
                    value="Age",
                    multi=False
                ),
            ]
        )
    ],
    body=True,
)

# Creating the application

# ------------------------------------------------------------------------------
# App layout

app.layout = dbc.Container(
    [
        html.H1("Toyota Corolla Prices"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls1, md=4),
                dbc.Col(dcc.Graph(id="violin_graph"), md=8),
            ],
            align="center",
        ),
        
        dbc.Row(
            [
                dbc.Col(controls2, md=4),
                dbc.Col(dcc.Graph(id="scatter_graph"), md=8),
            ],
            align="center",
        ),
        
    ],
    fluid=True,
)

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

@app.callback(
    Output(component_id = "violin_graph", component_property = "figure"),
    
    [Input(component_id = "cat_variable", component_property = "value")],
)

# Function to visualize chart -- returns go.Figure

def update_graph(cat):
    print(cat)
    
    df_local = df.loc[:, [cat, "Price"]]

    data = [
        go.Violin(
            x=df_local.loc[:, cat],
            y=df_local.loc[:, "Price"],
            box_visible=True,
        )
    ]

    layout = {"xaxis": {"title": cat}, "yaxis": {"title": "Price"}}

    return go.Figure(data=data, layout=layout)


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)







