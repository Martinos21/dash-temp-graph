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
import time
import os
import csv
import datetime as dt
from github import Auth
from github import Github
from gpiozero import CPUTemperature, DiskUsage
import psutil


max_size = 50

myq_temp = deque(maxlen=max_size)
myq_time = deque(maxlen=max_size)

query_temp = 'SELECT MEAN("value") AS mean_value, MIN("value") AS min_value, MAX("value") AS max_value, LAST("value") AS last_value FROM "°C" WHERE ("entity_id"=\'outdoor_temperature\')'
query_co2 = 'SELECT MEAN("value") AS mean_value, MIN("value") AS min_value, MAx("value") AS max_value, LAST("value") AS last_value FROM "state" WHERE ("entity_id" =\'co2\')'

#cpu = CPUTemperature()
#ram = psutil.virtual_memory().percent
#disk = DiskUsage()


def save_csv(vals, times):
    #vals, times = read_last_50_values
    times_list = list(times)
    vals_list = list(vals)

    data = list(zip(times_list, vals))

    project_directory = os.getcwd()

    output_directory = os.path.join(project_directory, 'output')
    csv_file_name = 'output_data.csv'

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    csv_file_path = os.path.join(output_directory, csv_file_name)

    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
    
        writer.writerow(['Column1', 'Column2'])
    
        writer.writerows(data)
    
    username = "Martehn03"
    token = "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"
    repo_name = 'dash-temp-graph'
    commit_message = "Publish file via script"
    file_path = csv_file_path

    g = Github(username, token)

    repo = g.get_user().get_repo(repo_name)

    with open(file_path, 'rb') as file:
        file_content = file.read()

    file_name = file_path.split("/")[-1]

    try:
        contents = repo.get_contents(file_name)

        repo.update_file(contents.path, commit_message, file_content, contents.sha)
        print("File updated successfully.")
        
    except Exception as e:
        
        repo.create_file(file_name, commit_message, file_content)
        print(f"Created new {file_name} in the repository.")
        


def read_last_50_values():
    host = "192.168.88.184"
    port = 8086
    user = "admin"
    password = "admin"
    database = "homeassistant"

    client = InfluxDBClient(host, port, user, password, database)

    query = f'SELECT * FROM "°C" WHERE ("entity_id"=\'outdoor_temperature\') ORDER BY time DESC LIMIT 50'

    result = client.query(query)
    
    values_list = []
    timestamps_list = []

    for point in result.get_points():
        
        value = point['value']
        timestamp = point['time']

        timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

        result = format(timestamp_datetime, "%H:%M:%S")

        values_list.append(value)
        timestamps_list.append(result)

        reversed_values_list = list(reversed(values_list))
        reversed_timestamps_list = list(reversed(timestamps_list))


    client.close()

    return reversed_values_list, reversed_timestamps_list

def database_query(query):
    host = "192.168.88.184"
    port = 8086
    user = "admin"
    password = "admin"
    database = "homeassistant"

    client = InfluxDBClient(host, port, user, password, database)

    result = client.query(query)
    points = result.get_points()

    for point in points:
        database_query.last_value = point['last_value']
        database_query.mean_value = point['mean_value']
        database_query.min_value = point['min_value']
        database_query.max_value = point['max_value']
        
    client.close()

mqttc = mqtt.Client()
mqttc.connect("192.168.88.105", 1884, 60 )

def on_connect(client, userdata, flags, rc):
    mqttc.subscribe("home-co2")

def on_message (client, userdata, msg):

    global home_co2

    msg.payload = msg.payload.decode("utf-8")

    if msg.topic == "home-co2":
        home_co2 = msg.payload

mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.loop_start()

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
            dcc.Interval(id='update', interval=1000*60, n_intervals=0),
            dbc.Row([dbc.Col(id="cpu-temp", children="Teplota cpu: "), 
                     dbc.Col(id="ram-usage", children="RAM: "), 
                     dbc.Col(id="disk-usage", children="Disk usage: ")]),
            html.Hr(),
            html.H1("Mereni teploty", style={'text-align':'center'}),
            html.Hr(),
            html.Div(id='actual-temp', style={'text-align':'center'}),
            html.Div(id='actual-co2', style={'text-align':'center'}),
            #dbc.Button('save csv', id='save-csv',n_clicks=0,className="d-grid gap-2 col-1 mx-auto", style={'align-items':'center'}),
            html.Hr(),
            dcc.Graph(id='real-time-graph', style={}),
            html.Hr(),
            dbc.Row([dbc.Col(highest_temp_card),dbc.Col(avg_temp_card), dbc.Col(lowest_temp_card)]),
            html.Div(id="output", hidden=True),
            
        ]
    )
)

@app.callback(
    Output('cpu-temp','children'),
    Input('update','n_intervals')
)

def span_update(_):
    cpu = CPUTemperature()
    return f"Teplota cpu: "+str(cpu.temperature)+" C"

@app.callback(
    Output('ram-usage','children'),
    Input('update','n_intervals') 
)

def span_update(_):
    ram = psutil.virtual_memory().percent
    return f"RAM: "+str(ram)+" %"

@app.callback(
    Output('disk-usage','children'),
    Input('update','n_intervals')
)

def span_update(_):
    disk = DiskUsage()
    return f"Disk usage: "+str(round(disk.usage,2))+" %"

@app.callback(
    Output('output','children'),
    Input('save-csv','n_clicks')
)

def save_csv_btn(n_clicks):
    vals, times = read_last_50_values()
    if n_clicks % 2 == 0 and n_clicks != 0:
        save_csv(vals,times)
    return 0

@app.callback(
        Output('actual-co2','children'),
        Input('update', 'n_intervals')
)

def update_cards(_):
    database_query(query_co2)

    return "Znecisteni je: " + str(database_query.last_value) + "ppm"

@app.callback(
        Output('actual-temp','children'),
        Input('update', 'n_intervals')
)

def update_cards(_):
    database_query(query_temp)

    return "Teplota je: " + str(database_query.last_value) + "°C" 

@app.callback(
    Output('real-time-graph', 'figure'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)
def update_real_time_graph(_):

    values, timestamps = read_last_50_values()

    data = [go.Scatter(x=list(timestamps), y=list(values), mode="lines+markers")]


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
    database_query(query_temp)

    return database_query.max_value 
    

@app.callback(
    Output('avg-temp', 'children'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)

def update_cards(_):
    database_query(query_temp)

    return format(database_query.mean_value, ".2f") + "°C"
    


@app.callback(
    Output('lowest-temp', 'children'),
    Input('update', 'n_intervals')
    #Input('input', 'value')
)

def update_cards(_):
    database_query(query_temp)

    return database_query.min_value 
    
    

if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0', debug=False, port=8059) #pro sdileni stranky v siti (testovano na windows)s