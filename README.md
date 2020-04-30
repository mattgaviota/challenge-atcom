# Instructions to test the API

In order to test this API you need python3 and pip3(optionally you can use venv) and following the next commands

1. git clone https://github.com/mattgaviota/challenge-atcom.git
2. cd challenge-atcom/atcom
3. (_OPTIONALLY_) python3 -m venv venv
4. (_OPTIONALLY_) source venv/bin/activate
5. pip3 install -r requirements.py
6. python app.py

If all run correctly now you can test the API using the following endpoints

    GET http://localhost:8099/searchEarthquake/getEarthquakesByDates

    body:
        {
            "fechaInicio": "2020-01-01",
            "fechaFin": "2020-03-02",
            "magnitudeMinima": "5.5"
        }

    GET http://localhost:8099/searchEarthquake/getEarthquakesByMagnitudes

    body:
        {
            "magnitudeMinima": "6.8",
            "magnitudeMaxima": "17.5"
        }
