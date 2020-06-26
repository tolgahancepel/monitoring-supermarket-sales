# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
from datetime import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import re

# get relative data folder
# PATH = pathlib.Path(__file__).parent
# DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_stylesheets = ['/assets/styles.css']
)

server = app.server

# A function to show big numbers

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

# Standart layout for charts

layout = dict(
    autosize=True,
    #automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
)


# Data Importing and Cleaning 
# --------------------------------------------------------------------------------------------

df = pd.read_csv("data/supermarket_sales.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["Time"] = pd.to_datetime(df["Time"])

# Daily Sales - Total and Average

df_mean = df.set_index('Date').groupby(pd.Grouper(freq='D'))["Total"].mean()
df_mean = pd.DataFrame(df_mean)

df_sum = df.set_index('Date').groupby(pd.Grouper(freq='D'))["Total"].sum()
df_sum = pd.DataFrame(df_sum)

# Total Prices by Product Line - for Pie Graph

total_prices_by_pline = df.groupby("Product line").sum()["Total"].sort_values(ascending=False)
total_prices_by_pline

# Product Line Sales

pline_daily = df.groupby(['Product line', 'City', pd.Grouper(key='Date', freq='W-MON')]).sum().reset_index().sort_values('Date')
    

# Creating charts without any input and callback
# --------------------------------------------------------------------------------------------

# Pie Graph - Percent of Product Lines

def update_pie_graph():
    
    layout_count = copy.deepcopy(layout)
    
    colors = ["#ff8b71",
              "#7dbca9",
              "#cba049",
              "#bed061",
              "#5f5c3b",
              "#989686"]
    
    labels = total_prices_by_pline.index
    values = total_prices_by_pline.values
    
    layout_count["title"] = "Percent of Product Lines"
    layout_count["title_x"] = 0.5
    layout_count["showlegend"] = True
    layout_count["autosize"] = True
    
    
    layout_count["legend"] = dict(
        x=0.03,
        y=-.05,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=10,
            color="black"
        ),
        bgcolor="#F9F9F9",
        bordercolor="Black",
        borderwidth=1,
        orientation='h'
    )
    
    figure = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))],
                       layout = layout_count)
    
    return figure

# App Layout
# --------------------------------------------------------------------------------------------
    
app.layout = html.Div(
    [
     
     # Navbar
     
     html.Div(
            className="pkcalc-banner",
            children=[
                
                html.A(
                    id="dash-logo",
                    children=[html.Img(src=app.get_asset_url("dash-logo.png"), style={'height':'45px'})],
                    href="/Portal",
                ),
                
                html.H2("Monitoring Supermarket Sales"),
                html.A(
                    id="gh-link",
                    children=["View on GitHub"],
                    href="https://github.com/tolgahancepel/monitoring-supermarket-sales",
                    style={"color": "white", "border": "solid 1px white"},
                ),
                html.Img(src=app.get_asset_url("GitHub-Mark-Light-64px.png")),
            ],
        ),
     
     #     
     
     # html.Div(
     #        className="container",
     #        children=[

     #        ],
     #    ),
     
     html.Div(
        [
            
            # Left Panel
            
            html.Div(
                [                    
                    html.Label("Daily Unit Price:"),
                    
                    dcc.Dropdown(
                        id='total_or_mean',
                        options=[
                            {'label': 'Total', 'value': 'Total'},
                            {'label': 'Mean', 'value': 'Mean'}
                        ],
                        value='Total'
                    ),
                    
                    html.Div(
                        [dcc.Graph(figure = update_pie_graph(), style={'height': 400})],
                        #id="countGraphContainer",
                        #className="pretty_container",
                    ),
                    
                    
                    
                ],
                className="pretty_container four columns",
                id="cross-filter-options",
            ),
                       
            html.Div(
                [
                    # Date Graph
                    
                    html.Div(
                            [
                                html.Div(
                                    [html.H4("$" + human_format(df["Total"].sum())), html.P("Total Sales")],
                                    id="wells", 
                                    className="mini_container",
                                    
                                ),
                                html.Div(
                                    [html.H4(df["Invoice ID"].count()), html.P("Transactions")],
                                    id="gas",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H4(df["Quantity"].sum()), html.P("Products")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H4("{:.2f}".format(df["Rating"].mean()) + " / 10"), html.P("Sales Rank")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                    
                    
                    html.Div(
                        [dcc.Graph(id="daily_unitprice", style={'height': 300})],
                        id="daily_graph",
                        className="pretty_container",
                    ),
                ],
                id="right-column",
                className="eight columns",
            ),
            
            
        ],
        className="row flex-display",
    ),
     
     
    # Second Row
     
    html.Div(
        [
            # Pie Chart
            
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id = "hourly_pline", style={'height': 400})],
                        #id="countGraphContainer",
                        #className="pretty_container",
                    ),
                    
                ],
                className="pretty_container six columns",
            ),
            
            # Something
            
            html.Div(
                [
                    html.Div(
                        [
                            
                            html.Div(
                                [html.Label("Product Line: ")],
                                
                                
                            ),
                            
                            dcc.Dropdown(
                                id='city_dropdown',
                                options=[
                                    {'label': 'Food and beverages', 'value': 'Food and beverages'},
                                    {'label': 'Fashion accessories', 'value': 'Fashion accessories'},
                                    {'label': 'Electronic accessories', 'value': 'Electronic accessories'},
                                    {'label': 'Sports and travel', 'value': 'Sports and travel'},
                                    {'label': 'Home and lifestyle', 'value': 'Home and lifestyle'},
                                    {'label': 'Health and beauty', 'value': 'Health and beauty'}
                                ],
                                value='Food and beverages'
                            ),
                                    
                            
                        ],
                        #id="wells",
                        className="mini_container",
                        
                    ),
                    
                    html.Div(
                        [dcc.Graph(id='weekly_pline', style = {'height': 300})],
                        #id="daily_graph",
                        className="pretty_container",
                    ),
                    
                    
                    
                ],
                className="eight columns",
            ),
        ],
        className="row flex-display",
    ),
    
    
    # Third Row
     
    html.Div(
        [
            # Something
            
            html.Div(
                [

                    
                    # html.Div(
                    #     [dcc.Graph(id = "hourly_pline", style={'height': 400})],
                    #     #id="countGraphContainer",
                    #     #className="pretty_container",
                    # ),
                    
                    
                    
                ],
                className="pretty-container twelve columns",
            ),
        ],
        className="row flex-display",
    ),
    
    
    
    
    
    
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

# Creating Callbacks
# --------------------------------------------------------------------------------------------

# Callback - Daily Sales Total and Average

@app.callback(
    Output("daily_unitprice", "figure"),
    [
        Input("total_or_mean", "value"),
    ],
)

def update_date_graph(value):
    layout_count = copy.deepcopy(layout)
    
    tmp = pd.DataFrame()
    
    my_color = ""
    
    if(value == "Mean"):
        tmp = df_mean
        my_color = "#654062"
    if(value == "Total"):
        tmp = df_sum
        my_color = "#ff6464"
    
        
    data = [
        dict(
            type="scatter",
            x=list(tmp.index),
            y=list(tmp["Total"]),
            fill='tozeroy',
            mode='lines',
            marker=dict(color=my_color),
            name="($) Cost",
            line=dict(
                shape='hvh'
            ),
        ),
    ]
    
    layout_count["title"] = "Daily Sales"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True
    
    layout_count["xaxis"] = dict(
        rangeselector=dict(
            buttons=list([
                  dict(count=7,
                      label="7d",
                      step="day",
                      stepmode="backward"),
                dict(count=15,
                      label="15d",
                      step="day",
                      stepmode="backward"),
                
                dict(count=1,
                      label="1m",
                      step="month",
                      stepmode="backward"),
                dict(count=2,
                      label="2m",
                      step="month",
                      stepmode="backward",
                      active=True),
                dict(step="all")    
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date",
        range = ['2019-03-15', '2019-03-30']
    )
            
    figure = dict(data=data, layout=layout_count)
    
    return figure


@app.callback(
    Output("weekly_pline", "figure"),
    [
        Input("city_dropdown", "value"),
    ],
)

def update_pline_graph(value):
    
    x_mandalay = pline_daily[(pline_daily["City"] == "Mandalay") & (pline_daily["Product line"] == value)].Date
    y_mandalay = pline_daily[(pline_daily["City"] == "Mandalay") & (pline_daily["Product line"] == value)].Total
    
    x_yangon = pline_daily[(pline_daily["City"] == "Yangon") & (pline_daily["Product line"] == value)].Date
    y_yangon = pline_daily[(pline_daily["City"] == "Yangon") & (pline_daily["Product line"] == value)].Total
    
    x_naypyitaw = pline_daily[(pline_daily["City"] == "Naypyitaw") & (pline_daily["Product line"] == value)].Date
    y_naypyitaw = pline_daily[(pline_daily["City"] == "Naypyitaw") & (pline_daily["Product line"] == value)].Total
    
    layout_count = copy.deepcopy(layout)
    
    fig = go.Figure(layout=layout_count)
    
    fig.add_trace(go.Scatter(x=x_mandalay, y=y_mandalay,
                             line=dict(color="#7dbca9", width=4),
                             line_shape="linear",
                             name = "Mandalay",
                             # fill='tozeroy',
                             connectgaps=True,))
    
    fig.add_trace(go.Scatter(x=x_yangon, y=y_yangon,
                             line=dict(color="#bed061", width=4),
                             line_shape="linear",
                             name = "Yangon",
                             # fill='tozeroy',
                             connectgaps=True,))
    
    fig.add_trace(go.Scatter(x=x_naypyitaw, y=y_naypyitaw,
                             line=dict(color="#ff8b71", width=4),
                             line_shape="linear",
                             name = "Naypyitaw",
                             # fill='tozeroy',
                             connectgaps=True,))
    
    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
            range = ['2019-01-07', '2019-03-30']
        ),
        
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=False,
        ),
        
        title = str(value) + " weekly sales",
        title_x = 0.5,
        #autosize=False,
        #showlegend=False,
        # plot_bgcolor='white'
        
        legend = dict(
            x=.25,
            y=-.3,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            ),
            bgcolor="#F9F9F9",
            bordercolor="Black",
            borderwidth=1,
            orientation='h'
        )
        
    )
    
    return fig


@app.callback(
    Output("hourly_pline", "figure"),
    [
        Input("city_dropdown", "value"),
    ],
)

def update_hourly_graph(value):
    # value = "Electronic accessories"
    
    hr_mandalay = df[(df["Product line"] == value) & (df["City"] == "Mandalay")]
    hr_mandalay = hr_mandalay.groupby(hr_mandalay["Time"].dt.hour)["Total"].sum().reset_index()
    
    hr_yangon = df[(df["Product line"] == value) & (df["City"] == "Yangon")]
    hr_yangon = hr_yangon.groupby(hr_yangon["Time"].dt.hour)["Total"].sum().reset_index()
    
    hr_naypyitaw = df[(df["Product line"] == value) & (df["City"] == "Naypyitaw")]
    hr_naypyitaw = hr_naypyitaw.groupby(hr_naypyitaw["Time"].dt.hour)["Total"].sum().reset_index()
    
    
    fig = make_subplots(rows=3, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.02
                    )
    
    # fig["layout"] = copy.deepcopy(layout)
    
    fig.append_trace(go.Scatter(x=hr_mandalay.Time, y=hr_mandalay.Total,
                             line=dict(color="#7dbca9", width=4),
                             line_shape="spline",
                             name = "Mandalay",
                             fill='tozeroy',
                             connectgaps=True,
                             ),
                     row = 1, col = 1)
    
    
    fig.append_trace(go.Scatter(x=hr_yangon.Time, y=hr_yangon.Total,
                             line=dict(color="#bed061", width=4),
                             line_shape="spline",
                             name = "Yangın",
                             fill='tozeroy',
                             connectgaps=True,
                             ),
                     row = 2, col = 1)
    
    fig.append_trace(go.Scatter(x=hr_naypyitaw.Time, y=hr_naypyitaw.Total,
                             line=dict(color="#ff8b71", width=4),
                             line_shape="spline",
                             name = "Naypyitaw",
                             fill='tozeroy',
                             connectgaps=True,
                             ),
                     row = 3, col = 1)
    
    
    fig.update_layout(
        # automargin = True
        autosize=True,
        hovermode="closest",
        margin=dict(l=30, r=30, b=20, t=40),
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        title = str(value) + " hourly sales",
        title_x = 0.25,
        
        legend = dict(
            x=.12,
            y=-.12,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            ),
            bgcolor="#F9F9F9",
            bordercolor="Black",
            borderwidth=1,
            orientation='h'
        ),
    )
    
    return fig




# Main
# --------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
