import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
from influxdb_client_3 import InfluxDBClient3, Point

mqttc = mqtt.Client()
mqttc.connect("192.168.88.105", 1884, 60)

def on_connect(client, userdata, flagsm, rc):
    print("Connected with result code "+str(rc))
    mqttc.subscribe("home-outdoortemp-analysis")

def on_message(client, userdata, msg):
    global temp_val
    temp_val = 0 

    msg.payload = msg.payload.decode("utf-8")

    if msg.topic == "home-outdoortemp-analysis":
        temp_val = msg.payload
        client = InfluxDBClient3(token="CCydvZsjTYeHXG3FpIfLZsT8FJqzlPdjqDkoI8jZWVfUpWlgJ8C0qgOjIJ0w7_k8APbKwPIlsjkLl6Yseev5iA==",
                         host="eu-central-1-1.aws.cloud2.influxdata.com",
                         org="Test_dev",
                         database="testicek")
        point = Point("measurement").field("temperature",temp_val)
        client.write(point)

mqttc.on_connect=on_connect
mqttc.on_message=on_message

mqttc.loop_start()
