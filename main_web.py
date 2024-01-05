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

present_hum_graph = 0
present_temp_graph = 0

highest_temp = None
lowest_temp = None

current_time = 0

time = []


max_size = 50

myq_temp = deque(maxlen=max_size)
myq_time = deque(maxlen=max_size)

client = InfluxDBClient(host="192.168.88.184", port = 8086, username="admin", password="admin", database="homeassistant")

def append_value(myq_temp, myq_time):
    myq_temp.append(present_temp_graph)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    myq_time.append(current_time)

#####################################################################
mqttc = mqtt.Client()
mqttc.connect("192.168.88.105", 1884, 60)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    mqttc.subscribe("home-outdoortemp-analysis")
    mqttc.subscribe("test1892")


def on_message(client, userdata, msg):

    global present_temp_graph
    global present_hum_graph
    global current_time
    global highest_temp
    global lowest_temp
    global time


    msg.payload = msg.payload.decode("utf-8")

    if msg.topic == "home-outdoortemp-analysis":
        present_temp = msg.payload
        present_temp_graph = float(present_temp)
        
        append_value(myq_temp,myq_time)



mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.loop_start()
####################################################################################
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
            dcc.Interval(id='update', interval=1000*10, n_intervals=0),
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

    query = 'SELECT MEAN("value") AS mean_value, MIN("value") AS min_value, MAX("value") AS max_value FROM "°C" WHERE ("entity_id"=\'outdoor_temperature\')'

    result = client.query(query)
    points = result.get_points()

    for point in points:
        max_value = format(point['max_value'], '.2f') + " ℃"
        

    return max_value

@app.callback(
    Output('avg-temp', 'children'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)

def update_cards(_):
    
    query = 'SELECT MEAN("value") AS mean_value, MIN("value") AS min_value, MAX("value") AS max_value FROM "°C" WHERE ("entity_id"=\'outdoor_temperature\')'

    result = client.query(query)
    points = result.get_points()

    for point in points:
        mean_value = format(point['mean_value'], '.2f') + " ℃"
        

    return mean_value


@app.callback(
    Output('lowest-temp', 'children'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)

def update_cards(_):
    
    query = 'SELECT MEAN("value") AS mean_value, MIN("value") AS min_value, MAX("value") AS max_value FROM "°C" WHERE ("entity_id"=\'outdoor_temperature\')'

    result = client.query(query)
    points = result.get_points()

    for point in points:
        min_value = format(point['min_value'], '.2f') + " ℃"
        

    return min_value

if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0', debug=False, port=8059) #pro sdileni stranky v siti (testovano na windows)