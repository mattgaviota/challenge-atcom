from datetime import datetime, timezone, timedelta
from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with, inputs
from requests import get as req_get
import json
import sqlite3

app = Flask(__name__)
api = Api(app)

connection = sqlite3.connect('earthquake.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS earthquakes (
        created_at timestamp PRIMARY KEY default (strftime('%s','now')),
        fecha_inicio date,
        fecha_fin date,
        magnitud_min real not null,
        magnitud_max real,
        salida text not null
    );''')
connection.commit()
connection.close()

BYDATEURL = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={startdate}&endtime={enddate}&minmagnitude={magnitude}"
BYMAGNITUDEURL = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude={minmagnitude}&maxmagnitude={maxmagnitude}"

resource_fields = {
    "mag": fields.Float,
    "place": fields.String,
    "time": fields.String,
    "updated": fields.String,
    "alert": fields.String,
    "status": fields.String,
    "tsunami": fields.Integer,
    "magType": fields.String,
    "type": fields.String,
    "title": fields.String
}


class Earthquake_by_date(Resource):
    def __init__(self):
        self.connection = sqlite3.connect('earthquake.db')
        self.cursor = self.connection.cursor()

    @marshal_with(resource_fields)
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('fechaInicio', type=inputs.date, required=True,
                            help='Start date to search')
        parser.add_argument('fechaFin', type=inputs.date, required=True,
                            help='End date to search')
        parser.add_argument('magnitudeMinima', type=float, required=True,
                            help='Limit to events with a magnitude larger than the specified minimum.')
        args = parser.parse_args(strict=True)
        url = BYDATEURL.format(
            startdate=args['fechaInicio'].strftime("%Y-%m-%d"), enddate=args['fechaFin'].strftime("%Y-%m-%d"), magnitude=args['magnitudeMinima'])
        response = req_get(url).json()
        # Save the search on the database
        self.cursor.execute('''INSERT INTO earthquakes (fecha_inicio, fecha_fin, magnitud_min, salida) values (?, ?, ?, ?)''', (
            args['fechaInicio'], args['fechaFin'], args['magnitudeMinima'], json.dumps(
                response)
        ))
        self.connection.commit()
        self.connection.close()
        # Make the response
        features = [element['properties'] for element in response['features']]
        for feature in features:
            feature['time'] = datetime.utcfromtimestamp(
                feature['time'] / 1000).strftime('%A, %B %d, %Y %I:%M:%S.%f %p')
            feature['updated'] = datetime.utcfromtimestamp(
                feature['updated'] / 1000).strftime('%A, %B %d, %Y %I:%M:%S.%f %p')
        return features


class Earthquake_by_magnitude(Resource):
    def __init__(self):
        self.connection = sqlite3.connect('earthquake.db')
        self.cursor = self.connection.cursor()

    @marshal_with(resource_fields)
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('magnitudeMinima', type=float,
                            help='Limit to events with a magnitude larger than the specified minimum.')
        parser.add_argument('magnitudeMaxima', type=float,
                            help='Limit to events with a magnitude smaller than the specified maximum.')
        args = parser.parse_args(strict=True)
        url = BYMAGNITUDEURL.format(
            minmagnitude=args['magnitudeMinima'], maxmagnitude=args['magnitudeMaxima'])
        response = req_get(url).json()
        # Save the search on the database
        self.cursor.execute('''INSERT INTO earthquakes (magnitud_min, magnitud_max, salida) values (?, ?, ?)''', (
            args['magnitudeMinima'], args['magnitudeMaxima'], json.dumps(response))
        )
        self.connection.commit()
        self.connection.close()
        # Make the response
        features = [element['properties'] for element in response['features']]
        for feature in features:
            feature['time'] = datetime.utcfromtimestamp(
                feature['time'] / 1000).strftime('%A, %B %d, %Y %I:%M:%S.%f %p')
            feature['updated'] = datetime.utcfromtimestamp(
                feature['updated'] / 1000).strftime('%A, %B %d, %Y %I:%M:%S.%f %p')
        return features


api.add_resource(Earthquake_by_date, '/searchEarthquake/getEarthquakesByDates')
api.add_resource(Earthquake_by_magnitude,
                 '/searchEarthquake/getEarthquakesByMagnitudes')

if __name__ == '__main__':
    app.run(debug=True, port=8099)
