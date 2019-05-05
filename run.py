import beer_app
from beer_app import app
import psycopg2






if __name__ == "__main__":
        conn = psycopg2.connect(host="localhost", dbname="BreweryDB" ,user="postgres" ,password="tashisonam" )

        app.run(debug=True)
