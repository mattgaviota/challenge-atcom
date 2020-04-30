from flask import Flask
from flask_restful import Api
from resources.earthquake import Earthquake_by_date, Earthquake_by_magnitude


app = Flask(__name__)
api = Api(app)

api.add_resource(Earthquake_by_date, '/searchEarthquake/getEarthquakesByDates')
api.add_resource(Earthquake_by_magnitude,
                 '/searchEarthquake/getEarthquakesByMagnitudes')

if __name__ == '__main__':
    app.run(debug=True, port=8099)
