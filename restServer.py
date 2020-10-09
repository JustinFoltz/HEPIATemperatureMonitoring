
import json
import pi_obj as pi
import requests
from flask import Flask


app = Flask(__name__)

@app.route('/pi/mean/locations')
def mean_by_location():
    """ 
    Route permettant de récupérer les valeurs des pi pour chaque salle
    @return : valeurs moyennes au format json
    """
    pi_ips = ["129.194.184.124", "129.194.184.125", "129.194.185.199"]
    pi_objs = get_all_pi_objs( pi_ips )
    means = pi.mean_pi_objs_by_field( pi_objs, "location" )
    return json.dumps(means)



def get_all_pi_objs( pi_ips ):
    """ 
    @description; Recupère toutes les valeurs des Raspberrypy
    @params: liste d'ip des Raspberry
    @return: dictionnaire des valeurs pis
    """
    pi_objs = []
    for ip in pi_ips:
        sensors = requests.get("http://"+ip+":5000/nodes/get_nodes_list")
        for sensor in json.loads(sensors.text) :
            measurement = requests.get("http://"+ip+":5000/sensors/"+str(sensor)+"/get_all_measures")
            try:
                pi_obj = pi.create_pi_obj( json.loads(measurement.text) ) 
                pi_objs.append( pi_obj )
            except ValueError:
                pass
    return pi_objs

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


