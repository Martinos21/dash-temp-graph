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

present_hum_graph = 0
present_temp_graph = 0

presenttemp = []
presenthum = []

highest_temp = None
lowest_temp = None

update = 0
current_time = 0

historical_values_temp = []
historical_values_hum = []
array_without_first = []
x_values = []
time = []
x_counter = 0


def create_limited_queue(max_size):
    return deque(maxlen=max_size)
"""
def append_random_value(queue):
    new_value = random.randint(1, 100)  # Adjust the range as needed
    queue.append(new_value)

def display_queue(queue):
    print("Current Queue:", list(queue))
"""
max_size = 50
my_queue = create_limited_queue(max_size)

myq_temp = deque(maxlen=max_size)
myq_time = deque(maxlen=max_size)


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
        
        historical_values_temp.append(present_temp_graph)
        myq_temp.append(present_temp_graph)

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        myq_time.append(current_time)

        highest_temp = max(historical_values_temp)
        lowest_temp = min(historical_values_temp)


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
        style={"width":"196px", "height":"105px"}
        
    )
    
)

lowest_temp_card = dbc.Card(
    dbc.CardBody(
        
        [
            html.H4("Lowest-temp"),
            html.Td(id= "lowest-temp"),

        ],
        style={"width":"196px", "height":"105px"}
        
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
            dbc.Row([dbc.Col(highest_temp_card), dbc.Col(lowest_temp_card)])

        ]
    )
)


@app.callback(
    Output('real-time-graph', 'figure'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)
def update_real_time_graph(_):

    global historical_values_temp, historical_values_hum, x_values, x_counter, highest_temp, lowest_temp
    
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

    return (str(highest_temp)+ "C")

@app.callback(
    Output('lowest-temp', 'children'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)

def update_cards(_):
    
    return (str(lowest_temp)+ "C")

if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0', debug=False, port=8059) #pro sdileni stranky v siti (testovano na windows)