from flask import Flask, render_template, request, flash
import psycopg2
from . import Beer_func
app = Flask(__name__)

# Config options - Make sure you created a 'config.py' file.
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']

# connection to postgresql
conn = psycopg2.connect(host="localhost", dbname="BreweryDB" ,user="postgres" ,password="your password" )

@app.route("/")
def home():
    graphJSON = Beer_func.bar_plot(conn)
    postalcode= Beer_func.get_postal_code(conn)
    bar = Beer_func.abvIbu_plot(conn)

    return render_template('index.html', graphJSON=graphJSON, postalcode=postalcode,plot =bar)




@app.route("/find_map", methods=['GET', 'POST'])
def find_map():
    cp = request.args.get('cp')
    brewery = Beer_func.find_brewery_map(conn,cp)
    if brewery is None:
        return render_template("not_found.html",zone=cp)

    Beer_func.save_map(conn,cp)
    return render_template("map.html")


@app.route("/beer_details", methods=['GET', 'POST'])

def beer_details_plot():
    b_name = request.args.get("beer")
    # get all the beer name
    beer_names =Beer_func.get_all_beer_name(conn)
    # replace " ' " in beer names
    b = b_name.replace("'","''")

    beer_graphJSON = Beer_func.beer_plot(conn,b)

    if b_name in beer_names:
        return render_template('beer_data.html',beer_graphJSON=beer_graphJSON,b_name=b_name)
    else:
        return render_template('not_found.html',b_name=b_name)

if __name__ == "__main__":

    app.run()
