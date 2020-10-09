
import paho.mqtt.client as paho
import sensortag
import requests
import time
import json

# paramètres du serveur rest fournissant les données pis
# -------------------------------------------------------
URL_RESTSERVER = "localhost"       
PORT_RESTSERVER = 5000                      
MEAN_ROUTE = "/pi/mean/locations"

# différents brokers sont disponibles
# possibilité de switcher de broker en modifiant la valeur de BROKER_IND
# la valeur doit être identique sur le subscriber 
# -------------------------------------------------------
BROKERS = ["broker.hivemq.com", "mosquitto.org", "test.mosquitto.org"]
BROKER_IND = 2
BROKER = BROKERS[BROKER_IND]
PORT_BROKER = 1883

# paramètres du capteur Bluetooth TI
# -------------------------------------------------------
MACADDRESS = "b0:b4:48:c9:97:07"
TAG = None

# intervale mimimum (minutes) entre deux émissions dans le broker
# utilisé pour les tests, 5minutes par défaut
# -------------------------------------------------------
DELTA_TIME = 1

# routine de collecte et d'émission de données dans le broker
# -------------------------------------------------------
def main():
    global TAG
    client= paho.Client("smarthepia")
    client.connect(BROKER,PORT_BROKER)

    hours_cmpt = 0
    day_cmpt = 0

    while True:
        print("\nSTART COLLECTING DATA")
        start_time = time.time()

        if TAG is None: TAG = connectTiSensor(MACADDRESS)
        if TAG is not None : publish_ti_data(TAG, client, "5minutes")

        pi_data = get_pi_average_by_location()
        publish_pi_data(client, pi_data, "5minutes")

        if hours_cmpt%60 == 0:
            if TAG is not None : publish_ti_data(TAG, client, "hour")
            publish_pi_data(client, pi_data, "hour")
            hours_cmpt = 0
        if day_cmpt%1440 == 0:
            if TAG is not None : publish_ti_data(TAG, client, "day")
            publish_pi_data(client, pi_data, "day")
            day_cmpt = 0
        
        hours_cmpt += DELTA_TIME
        day_cmpt += DELTA_TIME
        print("-----------------------------------")
        time_offset = min(time.time() - start_time, DELTA_TIME*60)
        time.sleep(DELTA_TIME*60 - time_offset)


def publish_pi_data( client, data, interval ):
    """
    @description: publie les données des capteurs pi dans le broker
    @param client: client broker dans lequel envoyer
    @param data: données à envoyer (dictionnaire des valeurs moyennes par salle)
    @param interval: interval d'émission pour construire le topic
    """
    topic = "hepia/pi/meanByLocation/"+interval
    publish(client, topic, data)


def get_pi_average_by_location():
    """
    @description: collecte les données sur le restserveur          
                  appelle la route <URL_RESTSERVER>:<PORT_RESTSERVER>/<MEAN_ROUTE>
    """
    pi_data_by_location = requests.get("http://"+URL_RESTSERVER+":"+str(PORT_RESTSERVER)+MEAN_ROUTE)
    return json.loads( pi_data_by_location.text )


def connectTiSensor(macAdress):
    """ 
    @description: établi une connexion avec un capteur TI
    @param macAdress: adresse MAC du capteur
    """
    try:
        tag = sensortag.SensorTag(macAdress)
    except: return None
    else: return tag
     

def enableTiSensors(tag):
    """
    @description: active les capteurs de température, d'humidité et de luminance 
                  d'un capteur TI avant de réaliser des lectures
    @param tag: identifiant du capteur TI (obtenu apres connexion)
    """
    tag.IRtemperature.enable()
    tag.humidity.enable()
    tag.lightmeter.enable()
    time.sleep(1.0)


def disableTiSensors(tag):
    """
    @description: déactive les capteurs de température, d'humidité et de luminance 
                  d'un capteur TI après lecture
    @param tag: identifiant du capteur TI (obtenu apres connexion)
    """
    tag.IRtemperature.disable()
    tag.humidity.disable()
    tag.lightmeter.disable()
    time.sleep(1.0)


def get_ti_data(tag):
    """
    @description: collectecte les informations d'un capteur TI
    @param tag: identifiant du capteur TI (obtenu apres connexion)
    """
    return [{
        'location': tag.version,
        'updateTime': time.time(),
        'data': {"temperature":tag.IRtemperature.read()[0],
                 "humidity":tag.humidity.read()[0],
                 "luminance": tag.lightmeter.read()}}]


def publish_ti_data(tag, client, interval):
    """
    @description: publie les données des capteurs ti dans le broker
    @param tag: identifiant du capteur TI (obtenu apres connexion) 
    @param client: client broker dans lequel envoyer
    @param interval: interval d'émission pour construire le topic 
    """
    enableTiSensors(tag)
    data = get_ti_data(tag)
    topic = "hepia/ti/values/"+interval
    publish(client, topic, data)
    disableTiSensors(tag)

def publish( client, topic, message ):
    """
    @description: publie des informations dans le broker
                  appelé par publish_pi_data et publish_ti_data
    @param client: client broker dans lequel envoyer
    @param topic: topic du message à envoyer (string)
    @param message: message à envoyer
    """
    json_message = json.dumps( message )
    print("data published on ", topic)
    client.publish( topic, json_message )


if __name__ == '__main__':
    main()