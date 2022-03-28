import json
import requests
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import pandas as pd
from pyproj import Transformer
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
import index

MAP_ID = "map-id"
BASE_LAYER_ID = "base-layer-id"
BASE_LAYER_DROPDOWN_ID = "base-layer-drop-down-id"
COORDINATE_CLICK_ID = "coordinate-click-id"

def irishgrid2xy(grid_ref):
    """
    Converts irish grid reference as string i.e. "N 15904 34671"
    to xy (easting northing) with an origin at the bottem
    left of grid "V"
    """

    # 5x5 grid letters, missing I
    grid = [("V", "W", "X", "Y", "Z"),
            ("Q", "R", "S", "T", "U"),
            ("L", "M", "N", "O", "P"),
            ("F", "G", "H", "J", "K"),
            ("A", "B", "C", "D", "E")]

    grid_ref = grid_ref.split(" ")
    letter = grid_ref[0].upper()
    easting = grid_ref[1]
    northing = grid_ref[2]

    if len(easting) == 5 & len(northing) == 5:
        for i in range(0,5):
            if letter in grid[i]:
                northing_corr = i
                easting_corr = (grid[i].index(letter))

    easting = '%s%s' % (easting_corr, easting)
    northing = '%s%s' % (northing_corr, northing)

    return easting, northing

def xy2irishgrid(x, y):
    """
    Convert x and y coordinate integers into irish grid reference string
    """
    x = str(x)
    y = str(y)

    grid = [("V", "W", "X", "Y", "Z"),
            ("Q", "R", "S", "T", "U"),
            ("L", "M", "N", "O", "P"),
            ("F", "G", "H", "J", "K"),
            ("A", "B", "C", "D", "E")]
    
    if (len(x) > 6) | (len(y) > 6):
        return "Not in IRE"

    if len(x) < 6:
        easting_corr = '0'
        easting = x
    else:
        easting_corr = x[0]
        easting = x[1:]

    if len(y) < 6:
        northing_corr = '0'
        northing = y
    else:
        northing_corr = y[0]
        northing = y[1:]
    try:
        letter = grid[int(northing_corr)][int(easting_corr)]
    except:
        return "Not in IRE"
    grid_ref = '%s %s %s' % (letter, easting, northing)
    return grid_ref

def xy2latlon(x, y):
    transformer = Transformer.from_crs("epsg:29903", "epsg:4326")
    lat, lon = transformer.transform(x , y)
    lat, lon = round(lat,5), round(lon,5)
    return lat, lon

def latlon2xy(lat, lon):
    transformer = Transformer.from_crs( "epsg:4326","epsg:29903")
    x, y = transformer.transform(lat, lon)
    x, y = int(x), int(y)
    return x, y

app = dash.Dash(__name__,
                url_base_pathname="/grid2latlon/",
                meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                ],
                prevent_initial_callbacks=True,
                suppress_callback_exceptions=True)

server = app.server
app.title = 'Irish Grid to Lat Lon'

@app.callback(Output("location-text", "children"), [Input(MAP_ID, "location_lat_lon_acc")])
def update_location(location):
    return "You are within {} meters of (lat,lon) = ({},{})".format(location[2], location[0], location[1])

@app.callback(Output("grid_ref_input_table", "style_table"),
              Output("xy_input_table", "style_table"), 
              Output("latlon_input_table", "style_table"), 
              Input("inputSelector", "value"))
def change_input_table(table):
    if table == "xy":
        return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
    elif table == "latlon":
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}

@app.callback(Output('latlon_input_table', 'data'),
              Input('latlon_input_table', 'data'),
              Input(MAP_ID, 'click_lat_lng'),
              Input('xy_input_table', 'data'),
              )
def update_on_click(latlonRows,click_lat_lon,xyRows):
    ctx = dash.callback_context
    triggeredID=ctx.triggered[0]['prop_id'].split('.')[0]
    if triggeredID == MAP_ID:
        for row in latlonRows:
            if row == {}:
                row['lat']=round(click_lat_lon[0],5)
                row['lon']=round(click_lat_lon[1],5)
                return latlonRows
    elif triggeredID == 'xy_input_table':
        latlonRows=[]
        for row in xyRows:
            try:
                lat, lon = xy2latlon(row['x'], row['y'])
                latlonRows.append({'lat':lat,'lon':lon})
            except:
                latlonRows.append({'lat':"",'lon':""})
        return latlonRows

    return latlonRows

@app.callback(Output('xy_input_table', 'data'),
              Input('grid_ref_input_table', 'data'),
              )
def update_on_click(gridRefRows):
    xyRows = []
    for row in gridRefRows:
        try:
            x, y = irishgrid2xy(row['grid_ref'])
            xyRows.append({'x':x,'y':y})
        except:
            xyRows.append({'x':"",'y':""})

    return xyRows
    
@app.callback(
    Output('output_table', 'data'),
    Input('latlon_input_table', 'data'))
def update_latlon(rows):
    for row in rows:
        try:
            lat, lon = row['lat'], row['lon']
            x, y = latlon2xy(lat, lon)
            row['x'], row['y'] = x, y
            row['grid_ref'] = xy2irishgrid(x, y)
        except:
            "fail"
    return rows

@app.callback(
    Output('markers', 'children'),
    Input('output_table', 'data'))
def update_output(rows):
    markers_list=[]
    i=0
    for row in rows:
        try:          
            marker = dl.Marker(position=[row['lat'], row['lon']], 
                               children=dl.Tooltip(
                                   [html.B("Marker {}".format(i)),
                                    html.Br(),
                                    "Grid Ref: {}".format(row['grid_ref']),
                                    html.Br(),
                                    "Lat: {:.2f} \u00b0".format(row['lat']),
                                    html.Br(),
                                    "Lon: {:.2f} \u00b0".format(row['lon']),
                                     html.Br(),
                                    "X: {}".format(row['x']),
                                    html.Br(),
                                    "Y: {}".format(row['y']),
                                     html.Br(),
                                    ]))
            markers_list.append(marker)
            i+=1
        except:
            "fail"
   
    return markers_list

# Create layout.
app.layout = html.Div(children=[
        html.Div(id='page-content',
                 children=index.create_layout(app)),
])

if __name__ == '__main__':
    app.run_server(debug=True)