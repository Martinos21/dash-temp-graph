import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import random
import dash_core_components
import pandas as pd
import paho.mqtt.client as mqtt
import dash_bootstrap_components as dbc
from datetime import datetime
from collections import deque
from influxdb import InfluxDBClient

max_size = 50

myq_temp = deque(maxlen=max_size)
myq_time = deque(maxlen=max_size)

def database_query():
    host = "192.168.88.184"
    port = 8086
    user = "admin"
    password = "admin"
    database = "homeassistant"

    client = InfluxDBClient(host, port, user, password, database)

# Combined query to select mean, min, and max values
    query = 'SELECT MEAN("value") AS mean_value, MIN("value") AS min_value, MAX("value") AS max_value, LAST("value") AS last_value FROM "°C" WHERE ("entity_id"=\'outdoor_temperature\')'

    
    result = client.query(query)
    points = result.get_points()

    for point in points:
        database_query.mean_value = point['mean_value']
        database_query.min_value = point['min_value']
        database_query.max_value = point['max_value']
        database_query.last_value = point['last_value']
        #print(f"Mean Value: {database_query.mean_value}, Min Value: {min_value}, Max Value: {max_value}")

    client.close()
def append_value(myq_temp, myq_time):
    myq_temp.append(database_query.last_value)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    myq_time.append(current_time)

highest_temp_card = dbc.Card(
    dbc.CardBody(
        
        [
            html.H4("Highest-temp"),
            html.Td(id= "highest-temp"),

        ],
        style={"width":"190px", "height":"105px"}
        
    )
    
)

avg_temp_card = dbc.Card(
    dbc.CardBody(
        
        [
            html.H4("AVG-temp"),
            html.Td(id= "avg-temp"),

        ],
        style={"width":"190px", "height":"105px"}
        
    )
    
)

lowest_temp_card = dbc.Card(
    dbc.CardBody(
        
        [
            html.H4("Lowest-temp"),
            html.Td(id= "lowest-temp"),

        ],
        style={"width":"190px", "height":"105px"}
        
    )
    
)

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container(
    html.Div(
        children=[
            dcc.Interval(id='update', interval=1000*600, n_intervals=0),
            html.H1("Mereni teploty", style={'text-align':'center'}),
            html.Hr(),
            dcc.Graph(id='real-time-graph'),
            html.Hr(),
            dbc.Row([dbc.Col(highest_temp_card),dbc.Col(avg_temp_card), dbc.Col(lowest_temp_card)])

        ]
    )
)


@app.callback(
    Output('real-time-graph', 'figure'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)
def update_real_time_graph(_):
    
    database_query()
    append_value(myq_temp,myq_time)

    data = [go.Scatter(x=list(myq_time), y=list(myq_temp), mode="lines+markers")]


    layout = go.Layout(
        title='Real-Time Graph with Historical Data',
        xaxis=dict(title='Time'),
        yaxis=dict(title='Value'),
        uirevision=0
    )

    figure = go.Figure(data=data, layout=layout)


    return figure

@app.callback(
    Output('highest-temp', 'children'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)

def update_cards(_):
    database_query()

    return database_query.max_value
    

@app.callback(
    Output('avg-temp', 'children'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)

def update_cards(_):
    database_query()

    return format(database_query.mean_value, ".2f")
    


@app.callback(
    Output('lowest-temp', 'children'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)

def update_cards(_):
    database_query()

    return database_query.min_value
    
    

if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0', debug=False, port=8059) #pro sdileni stranky v siti (testovano na windows)