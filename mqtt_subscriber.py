from flask import Flask, render_template, request
from flask_mqtt import Mqtt
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from bson.json_util import dumps
import pymongo
import eventlet
import json
import datetime
import time

eventlet.monkey_patch()

# Database connection
client = pymongo.MongoClient("mongodb://user:test@localhost:27017/")
db = client.smartHepia
col_con = db.connexion
col_avg = db.average

app = Flask(__name__)

BROKERS = ["broker.hivemq.com", "mosquitto.org", "test.mosquitto.org"]
BROKER_IND = 2
BROKER = BROKERS[BROKER_IND]
PORT_BROKER = 1883

app.config['SECRET'] = 'my secret key 2'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = BROKER
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

mqtt = Mqtt(app)
socketio = SocketIO(app)

NUMBER_CONNEXIONS   = 0

PI = {"sensor": "pi",
      "locations": ["A532", "A533", "A503", "A507", "A406", "A432", "A433", "A434", "A400", "A401", "A402", "A403", "A404"],
      "durations": ["5minutes", "hour", "day"]}
mqtt.subscribe("hepia/pi/meanByLocation/5minutes")
mqtt.subscribe("hepia/pi/meanByLocation/hour")
mqtt.subscribe("hepia/pi/meanByLocation/day")


TI = {"sensor": "ti",
      "locations": ["CC2650"],
      "durations": ["5minutes", "hour", "day"]}
mqtt.subscribe("hepia/ti/values/5minutes")
mqtt.subscribe("hepia/ti/values/hour")
mqtt.subscribe("hepia/ti/values/day")


SENSORS = [PI, TI]

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on('connect')
def handle_message():
    print("client connection")
    global NUMBER_CONNEXIONS, SENSORS
    NUMBER_CONNEXIONS += 1
    socketio.emit('sensors', data=SENSORS, namespace='/', room = request.sid)
    socketio.emit('number_connexions', data=NUMBER_CONNEXIONS)

@socketio.on('disconnect')
def handle_message():
    print("client disconect")
    global NUMBER_CONNEXIONS
    NUMBER_CONNEXIONS -= 1
    socketio.emit('number_connexions', data=NUMBER_CONNEXIONS)
    
@socketio.on('subscribe')
def handle_message(parameters):
    room = parameters["room"]
    from_timestamp = parameters['from']

    print("client subscription in room : ", room)
    join_room(room)

    if from_timestamp != "":
        history = getHistory(from_timestamp, room)
        for data in history:
             socketio.emit("measure", data=data, room=data["tag"])

def getParamsInRoom(room):
    pArr = room.split("/")
    return pArr[0], pArr[1], pArr[2]

def getHistory(from_timestamp, tag):
    return list(db.col_avg.find({'tag': tag, 'timestamp':{"$gt": from_timestamp}}, {'_id': False}))

@socketio.on('unsubscribe')
def handle_message(data):
    print("client leave room : ", data["room"])
    leave_room( data["room"] )

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    dataset = mqtt_serializer(message)
    print("data receive from ", message.topic)
    for data in dataset:
        socketio.emit("measure", data=data, room=data["tag"])
        db.col_avg.insert_one(data)

def send_data_to_client(room, data):
    print(data)
    location = data["location"]
    update_time = data["updateTime"]

def mqtt_serializer(message):
    dataset = []
    topic = message.topic.split("/")
    sensor = sensor = topic[1]
    interval = topic[-1]
    str_dataset = str(message.payload.decode("utf-8"))
    raw_dataset = json.loads(str_dataset)
    for data in raw_dataset:
        location = data["location"]
        update_time = data["updateTime"]
        room = sensor+"/"+location+"/"+interval
        dataset.append({"tag":room, "timestamp":update_time, "measure":data["data"]})
    return dataset


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, use_reloader=False, debug=False)


