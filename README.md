# Grid 2 Lat Lon

Grid2LatLon is a helpful tool to bulk convert between the different location coordinate systems used in Ireland - Irish Grid References, XY (Easting,Northing) and LatLon.

It is built using the Python [Python Dash](https://dash.plotly.com/) web framework and makes use of the [pyproj](https://pyproj4.github.io/pyproj/stable//) cartographic projections and coordinate transformations library. PyProj does not have an api for converting to between Irish Grid References and XY coordinates, for which conversion scripts were developed.

## Requirements

[Generate your own MAPBOX_TOKEN](https://docs.mapbox.com/help/getting-started/) and set it as an environmental variable on your machine.
```
export MAPBOX_TOKEN=<your_mapbox_token>
```

## Getting Started
Clone the repository and install dependencies.

```
git clone https://github.com/dancasey-ie/Grid2LatLon
cd Grid2LatLon
```
You can run the application using docker-compose, docker or as a python application, each detailed below.

For each of the methods below the app will be running at [localhost:8080](http://localhost:8080/grid2latlon).

### Using docker-compose.yml
If you have both [docker](https://www.docker.com/get-started) and [docker-compose](http://localhost:8080/grid2latlon) installed then:
```
docker-compose up -d
```

### Using Dockerfile
If you have [docker](https://www.docker.com/get-started) installed then:
```
docker build -t grid2latlon .
docker run -it -p 8080:8080 -e MAPBOX_TOKEN=${MAPBOX_TOKEN} --name grid2latlon grid2latlon
```
### Using Python (venv)

```
python -m venv ./env
source env/bin/activate # for windows: env/Scripts/activate
pip install -r dash_app/requirements.txt
python dash_app/app.py

```

## Contributing

Dan Casey
