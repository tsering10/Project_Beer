import folium
from folium.plugins import MarkerCluster
import plotly
import plotly.graph_objs as go
import plotly.plotly as py
import json


def bar_plot(conn):

    cur = conn.cursor()


    # Get the count of lager
    request = "SELECT Count(shortname) as Lager FROM style WHERE shortname LIKE '%Lager%' "
    cur.execute(request)

    lager = [elem[0] for elem in cur.fetchall()]

    # get the count of ALE
    request1 = "SELECT Count(shortname) as ALE  FROM style WHERE shortname LIKE '%Ale%' "
    cur.execute(request1)

    Ale = [elem[0] for elem in cur.fetchall()]

    # get the count of belgian
    request2 = "SELECT Count(shortname) as belgian  FROM style WHERE shortname LIKE '%Belgian%' "
    cur.execute(request2)

    belgian = [elem[0] for elem in cur.fetchall()]

    # get the count of cider

    request3 = "SELECT Count(shortname) as Cider  FROM style WHERE shortname LIKE '%Cider%' "
    cur.execute(request3)

    cider = [elem[0] for elem in cur.fetchall()]

    # get the count of Bitter

    request3 = "SELECT Count(shortname) as Bitter  FROM style WHERE shortname LIKE '%Bitter%' "
    cur.execute(request3)

    bitter = [elem[0] for elem in cur.fetchall()]

    request4 = "SELECT Count(shortname) as IPA  FROM style WHERE shortname LIKE '%IPA%' "
    cur.execute(request4)

    ipa = [elem[0] for elem in cur.fetchall()]

    # get count of Porter

    request5 = "SELECT Count(shortname)   FROM style WHERE shortname LIKE '%Porter%' "
    cur.execute(request5)

    porter = [elem[0] for elem in cur.fetchall()]



     # form a list of all beer style
    beer_style = [lager,ipa, Ale,belgian,cider,bitter,porter]
    # single list containing all the beer styles
    flat_list = [item for sublist in beer_style for item in sublist]

    # create plotly bar graph
    trace0 =go.Bar(
        x=['Lager','IPA', 'ALE', 'Belgian','Cider','Bitter','Porter'],
        y= flat_list,
        text=['style: Lager','style: India pale ale','style: ALE', 'style:Belgian','style:Cider','style:Bitter','style: Porter'],
        marker=dict(
            color=['rgba(204,48,204,1)', 'rgba(222,45,38,0.8)',
                   'rgba(49,130,189,1)','rgba(50, 171, 96, 0.7)','rgb(8,48,107)','rgb(55, 83, 109)','rgb(26, 118, 255)'],

            line=dict(
                color='rgb(8,48,107)',
                width=1.5,
            )
        ),
            opacity=0.6
    )

    data = [trace0]

    layout = go.Layout(
        title='Most Commonly Produced Beer Style',
        xaxis=dict(
            title = 'Style',
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='Number Produced',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),

    )

    fig = go.Figure(data=data, layout=layout)
    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents



    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def get_postal_code(conn):

    cur = conn.cursor()
    request = "select distinct postalcode from location"
    cur.execute(request)

    postalcode = [elem[0] for elem in cur.fetchall()]

    cur.close()

    return postalcode

# create interative map using folium

def find_brewery_map(conn,cp):
    cur = conn.cursor()
    cur.execute("SELECT name, locality,phone,region,latitude,longitude FROM location WHERE postalcode ='{}' ".format(cp))

    while True:
      tple = cur.fetchone()
      if tple is None :
        break
      is_find = tple[0]
      if is_place_available(conn, cp):
        return is_find
    return None

def is_place_available(conn, cp):
    cur = conn.cursor()

    request = "SELECT * FROM location WHERE postalcode='{}' "
    cur.execute(request.format(cp))

    if cur.fetchone() is None : return False

    request = "SELECT * FROM location WHERE postalcode ='{}' "
    cur.execute(request.format(cp))

    return cur.fetchone()

def save_map(conn,cp):
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(latitude) FROM location ")
    lat_m = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(longitude) FROM location ")
    lon_m = cursor.fetchone()[0]

    rest_map = folium.Map(location=[lat_m,lon_m],zoom_start=3, tiles='OpenStreetMap')
    marker_cluster = folium.plugins.MarkerCluster().add_to(rest_map)

    cursor.execute("SELECT name,phone,latitude,longitude FROM location WHERE postalcode ='{}' ".format(cp))
    for elem in cursor.fetchall():
        if elem[2] is not None:
            marker = folium.Marker(location=(round(elem[2],6),round(elem[3],6)), popup=elem[0].strip().replace("'","")+' '+str(elem[1])[:15]).add_to(marker_cluster)
    rest_map.save('beer_app/templates/map.html')

# create a abv vs Ibu plotly graph

def abvIbu_plot(conn):

    cur = conn.cursor()
    request = "SELECT abvmax from style"
    cur.execute(request)

    abvmax = [elem[0] for elem in cur.fetchall()]

    request1 = "SELECT ibumax from style"
    cur.execute(request1)

    ibumax = [elem[0] for elem in cur.fetchall()]

    request2 = "SELECT shortname from style "
    cur.execute(request2)

    shortname = [elem[0] for elem in cur.fetchall()]

    fig = {
        'data': [
      		{
      			'x': abvmax ,
            	'y': ibumax,
            	'text': shortname,
            	'mode': 'markers'

            	}

        ],
        'layout': {'title': "Beer ABV vs IBU",
            'xaxis': {'title': 'Alcohol by volumn (ABV)'},
            'yaxis': {'title': "International bitterness units(IBU)"}
        }
    }

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    return graphJSON

# get all the beers

def get_all_beer_name(conn):
    cur = conn.cursor()
    request = "SELECT distinct name from beer order by name"
    cur.execute(request)

    beer_names = [elem[0] for elem in cur.fetchall()]



    return beer_names


# creating a beer plot for the selected beer

def beer_plot(conn, b):
    cur = conn.cursor()

    request = "select abvmax from beer INNER JOIN style ON beer.styleid = style.styleid where beer.name = '{}' ".format(b)
    cur.execute(request)

    beer_abv = [elem[0] for elem in cur.fetchall()]

    request1 = "select ibumax from beer INNER JOIN style ON beer.styleid = style.styleid where beer.name = '{}' ".format(b)
    cur.execute(request1)

    beer_ibu = [elem[0] for elem in cur.fetchall()]

    rquery = "select srmmax from beer INNER JOIN style ON beer.styleid = style.styleid where beer.name = '{}' ".format(b)
    cur.execute(rquery)
    beer_srm = [elem[0] for elem in cur.fetchall()]



    # form a list of all beer data
    beer_data = [beer_abv, beer_ibu, beer_srm]
    flat_list = [item for sublist in beer_data for item in sublist]

    trace0 =go.Bar(
       x=['ABV','IBU', 'SRM'],
       y= flat_list,
       text=['Alcohol By Volumn','International Bitterness Unit','Standard Reference Method'],
       marker=dict(
           color=['rgba(204,48,204,1)', 'rgba(222,45,38,0.8)',
                  'rgba(50, 171, 96, 0.7)','rgb(55, 83, 109)'],

           line=dict(
               color='rgb(8,48,107)',
               width=1.5,
           )
       ),
           opacity=0.6
   )

    data = [trace0]

    layout = go.Layout(
       title='',
       xaxis=dict(
           title = '',
           tickfont=dict(
               size=14,
               color='rgb(107, 107, 107)'
           )
       ),
       yaxis=dict(
           title='',
           titlefont=dict(
               size=16,
               color='rgb(107, 107, 107)'
           ),
           tickfont=dict(
               size=14,
               color='rgb(107, 107, 107)'
           )
       ),

   )

    fig = go.Figure(data=data, layout=layout)

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
