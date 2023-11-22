import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import random
import dash_core_components
import pandas as pd
import paho.mqtt.client as mqtt
import dash_bootstrap_components as dbc

present_hum_graph = 0
present_temp_graph = 0

presenttemp = []
presenthum = []

highest_temp = None
lowest_temp = None

update = 0

historical_values_temp = []
historical_values_hum = []
x_values = []
x_counter = 0

#####################################################################
mqttc = mqtt.Client()
mqttc.connect("broker.hivemq.com", 1883, 60)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    mqttc.subscribe("home-temp-val")


def on_message(client, userdata, msg):

    global present_temp_graph
    global present_hum_graph

    msg.payload = msg.payload.decode("utf-8")

    if msg.topic == "home-temp-val":
        present_temp = msg.payload
        present_temp_graph = float(present_temp)



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
            dcc.Interval(id='update', interval=1000*30, n_intervals=0),
            html.H1("Klimakomora", style={'text-align':'center'}),
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

    historical_values_temp.append(present_temp_graph)
    historical_values_hum.append(present_hum_graph)

    highest_temp = max(historical_values_temp)
    lowest_temp = min(historical_values_temp)

    print (lowest_temp)

    

    x_values.append(x_counter)
    x_counter += 1

    data = {
        'x': x_values,
        'present-temp': historical_values_temp,
        #'present-hum': historical_values_hum,
    }

    df = pd.DataFrame.from_dict(data)
    
    traces = []
    for column in df.columns[1:]:
        trace = go.Scatter(
            x=df['x'],
            y = df[column],
            mode = 'lines+markers',
            name = column
        )
        traces.append(trace)


    layout = go.Layout(
        title='Real-Time Graph with Historical Data',
        xaxis=dict(title='Time'),
        yaxis=dict(title='Value'),
        uirevision=0
    )

    figure = go.Figure(data=traces, layout=layout)

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
    app.run_server(debug=True)