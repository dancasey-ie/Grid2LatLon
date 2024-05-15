import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash_core_components as dcc
import dash_leaflet as dl
import os

# Mapbox setup
mapbox_url = "https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{{z}}/{{x}}/{{y}}{{r}}?access_token={access_token}"
try:
    mapbox_token = os.environ.get('MAPBOX_TOKEN')
except:
    print("Failed to locate MAPBOX_TOKEN environmental variable. Register a token at https://docs.mapbox.com/help/getting-started/access-tokens/")
mapbox_ids = ["light-v9", "dark-v9", "streets-v9",
              "outdoors-v9", "satellite-streets-v9"]

MAP_ID = "map-id"
BASE_LAYER_ID = "base-layer-id"
BASE_LAYER_DROPDOWN_ID = "base-layer-drop-down-id"
COORDINATE_CLICK_ID = "coordinate-click-id"

num_points = 50

grid_ref_input_table = dash_table.DataTable(
    id='grid_ref_input_table',
    columns=([
        {'id': 'grid_ref', 'name': 'Irish Grid Ref', 'type': 'text'}
    ]),
    data=[dict(grid_refs="") for i in range(1, num_points+1)],
    style_table={'display': 'none'},
    editable=True)

xy_input_table = dash_table.DataTable(
    id='xy_input_table',
    columns=([{'id': 'x', 'name': 'X', 'type': 'numeric'},
             {'id': 'y', 'name': 'Y', 'type': 'numeric'}
             ]),
    data=[dict() for i in range(1, num_points+1)],
    style_table={'display': 'none'},
    editable=True)

latlon_input_table = dash_table.DataTable(
    id='latlon_input_table',
    columns=([{'id': 'lat', 'name': 'Lat', 'type': 'numeric'},
             {'id': 'lon', 'name': 'Lon', 'type': 'numeric'}]),
    data=[dict() for i in range(1, num_points+1)],
    style_table={'display': 'block'},
    editable=True)

output_table = dash_table.DataTable(
    id='output_table',
    columns=([
        {'id': 'grid_ref', 'name': 'Irish Grid Ref'},
        {'id': 'x', 'name': 'X'},
        {'id': 'y', 'name': 'Y'},
        {'id': 'lat', 'name': 'Lat'},
        {'id': 'lon', 'name': 'Lon'},
    ]),
    data=[dict(index=i)for i in range(1, num_points+1)],
    editable=False,
    style_cell={
        'height': 'auto',
        # all three widths are needed
        'minWidth': '100px',
                    # 'width': '180px',
                    'maxWidth': '180px',
                    'whiteSpace': 'normal'
    }
)


def create_layout(app):

    return dbc.Container(
        className="grid2latlon_container",
        children=[
            html.H1(
                """Bulk Convert Between Irish Grid References, XY Cordinates and Latitude, Longitude"""),
            html.P(
                "Helpful tool to convert between some of the different coordinate systems used in Ireland.",
                className='text-center'
                    ),
            html.P(
                [
                    '"Hi there I hope you find this app useful. Just letting you know that this app is not actively maintained. It has been working away for the past few years and I will happily keep it live as people seem to find it useful. Be patient if you are converting many points.',
                    " The underlying code can be found on  ",
                    html.A("Github", href="https://github.com/dancasey-ie/Grid2LatLon", target="_blank"),
                    ". For converting anything other that Irish Grid coordinates with the leading letter, check out my ",
                    html.A("batch-coordinate-converter", href="https://dancasey.ie/batch-coordinate-converter/", target="_blank"), " app.",
                    '" - ',
                    html.A("Dan Casey", href="https://dancasey.ie", target="_blank"),
                    " (May 2024)"
                ],
                className='text-center'
            ),
            dbc.Row(children=[
                dbc.Col(
                    className="col-12 col-md-6 col-lg-3 mt-4",
                    children=[
                        html.H4("How to Convert"),
                              html.H5("Option 1: Click on Map"),
                                html.P("Click on the map to add a location for converting."),
                                html.H5("Option 2: Use Input Table"),
                                html.P("Select input type."),
                                dcc.RadioItems(
                                    id="inputSelector",
                                    options=[
                                        {'label': ' Lat, Lon e.g. 52.01, -9.57', 'value': 'latlon'},
                                        {'label': ' X,  Y e.g. 92315, 85538', 'value': 'xy'},
                                        {'label': ' Irish Grid Ref e.g. V 92315 85538', 'value': 'grid_ref'}],

                                    value='latlon',
                                    labelStyle={'display': 'block'}),
                                html.P("Manually enter or paste in coordinates into the Input Table"),
                                html.P("Note: To select multiple cells in the output table hold down Shift while selecting, like in Excel.")
                    ]),
                dbc.Col(
                    className="col-12 col-md-6 col-lg-9 mt-4",
                    children=[
                        dl.Map(id=MAP_ID,
                               style={'width': '100%', 'height': '500px'},
                               center=[53.0, -8.0],
                               zoom=6,
                               children=[
                                   dl.LayerGroup(id="markers"),
                                   dl.LocateControl(options={'locateOptions': {
                                       'enableHighAccuracy': True}}),
                                   dl.MeasureControl(position="topleft", primaryLengthUnit="kilometers", primaryAreaUnit="hectares",
                                                     activeColor="#214097", completedColor="#972158"),
                                   dl.LayersControl(
                                       [dl.BaseLayer([
                                           dl.TileLayer(url=mapbox_url.format(
                                               id=mapbox_id, access_token=mapbox_token)),

                                       ],
                                           name=mapbox_id,
                                           checked=mapbox_id == "outdoors-v9") for mapbox_id in mapbox_ids]
                                   )
                               ]),
                    ]),
            ]),

            html.Div(id="location-text"),
            html.Div(id=COORDINATE_CLICK_ID),
            html.Div([

                html.Div(id="inputDiv"),

                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.B("Input Table"),
                            grid_ref_input_table,
                            xy_input_table,
                            latlon_input_table, ]
                        ),
                        className='col-12 col-md-6 col-lg-3 text-center'),
                    dbc.Col(
                        html.Div(children=[
                            html.B("Output Table"),
                            output_table,
                        ]
                        ),
                        className='col-12 col-md-6 col-lg-9 text-center'),
                ])
            ]),
        ])
