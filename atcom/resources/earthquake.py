from datetime import datetime
from flask_restful import abort, fields, inputs, marshal_with, reqparse, Resource
from requests import get as req_get
from sqlite3 import DatabaseError
from .database import Database
import json


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


class Earthquake(Resource):
    def __init__(self):
        try:
            self.database = Database()
            self.connection, self.cursor = self.database()
            self.parser = self.init_parser()
        except Exception:
            abort(500, message="Error on the database connection")

    @marshal_with(resource_fields)
    def get(self):
        pass

    def insert_on_database(self, kwargs):
        pass

    def init_parser(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        return parser

    def validate(self, kwargs):
        pass

    def parse_response(self, response):
        features = [element['properties'] for element in response['features']]
        for feature in features:
            feature['time'] = datetime.utcfromtimestamp(
                feature['time'] / 1000).strftime('%A, %B %d, %Y %I:%M:%S.%f %p')
            feature['updated'] = datetime.utcfromtimestamp(
                feature['updated'] / 1000).strftime('%A, %B %d, %Y %I:%M:%S.%f %p')
        return features


class Earthquake_by_date(Earthquake):

    def init_parser(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('fechaInicio', type=inputs.date, required=True,
                            help='Start date to search')
        parser.add_argument('fechaFin', type=inputs.date, required=True,
                            help='End date to search')
        parser.add_argument('magnitudeMinima', type=float, required=True,
                            help='Limit to events with a magnitude larger than the specified minimum.')
        return parser

    def insert_on_database(self, kwargs):
        try:
            query = '''INSERT INTO earthquakes (fecha_inicio, fecha_fin, magnitud_min, salida) values (?, ?, ?, ?)'''
            self.cursor.execute(
                query, (kwargs['fechaInicio'], kwargs['fechaFin'], kwargs['magnitudeMinima'], json.dumps(kwargs['response'])))
            self.connection.commit()
            self.connection.close()
        except DatabaseError:
            abort(500, message='Request could not be stored on database')

    def validate(self, kwargs):
        if kwargs['magnitudeMinima'] > 12 or kwargs['magnitudeMinima'] < 1:
            abort(
                422, message='magnitudeMinima must be greater or equal to 1 and less or equal to 12')
        if kwargs['fechaInicio'] > kwargs['fechaFin']:
            abort(422, message='fechaInicio must be before fechaFin')
        if kwargs['fechaFin'] > datetime.now():
            abort(422, message='fechaFin must be before or equal to today')
        if kwargs['fechaInicio'] < datetime.strptime('2010-01-01', '%Y-%m-%d'):
            abort(422, message='fechaFin must be after or equal to 2010-01-01')

    @marshal_with(resource_fields)
    def get(self):
        args = self.parser.parse_args(strict=True)
        self.validate(args)
        url = BYDATEURL.format(
            startdate=args['fechaInicio'].strftime("%Y-%m-%d"), enddate=args['fechaFin'].strftime("%Y-%m-%d"), magnitude=args['magnitudeMinima'])
        args['response'] = req_get(url).json()
        # Save the search on the database
        self.insert_on_database(args)

        return self.parse_response(args['response'])


class Earthquake_by_magnitude(Earthquake):

    def init_parser(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('magnitudeMinima', type=float,
                            help='Limit to events with a magnitude larger than the specified minimum.')
        parser.add_argument('magnitudeMaxima', type=float,
                            help='Limit to events with a magnitude smaller than the specified maximum.')
        return parser

    def insert_on_database(self, kwargs):
        try:
            query = '''INSERT INTO earthquakes (magnitud_min, magnitud_max, salida) values (?, ?, ?)'''
            self.cursor.execute(
                query, (kwargs['magnitudeMinima'], kwargs['magnitudeMaxima'], json.dumps(kwargs['response'])))
            self.connection.commit()
            self.connection.close()
        except DatabaseError:
            abort(500, message='Request could not be stored on database')

    def validate(self, kwargs):
        if kwargs['magnitudeMinima'] > kwargs['magnitudeMaxima'] or kwargs['magnitudeMinima'] < 1:
            abort(
                422, message='magnitudeMinima must be greater or equal to 1 and smaller of magnitudeMaxima')
        if kwargs['magnitudeMaxima'] > 12:
            abort(
                422, message='magnitudeMaxima must be greater than magnitudeMinima and less or equal to 12')

    @marshal_with(resource_fields)
    def get(self):
        args = self.parser.parse_args(strict=True)
        self.validate(args)
        url = BYMAGNITUDEURL.format(
            minmagnitude=args['magnitudeMinima'], maxmagnitude=args['magnitudeMaxima'])
        args['response'] = req_get(url).json()
        # Save the search on the database
        self.insert_on_database(args)
        return self.parse_response(args['response'])
