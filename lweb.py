import dash_leaflet as dl
from dash import Dash, html, dcc,Input, Output, State,ctx
import pandas as pd
import polyline, json, requests, math
import plotly.graph_objects as go

app = Dash(__name__)

headers = {'X-Goog-Api-Key': 'AIzaSyDelhuHFr6dQ0o-kmK2c3_FutPat294KUc','X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'}
headers2 = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': 'AIzaSyDelhuHFr6dQ0o-kmK2c3_FutPat294KUc',
    'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.legs,geocodingResults',
}

def createSimpleRoute(Origin, Destination, Backhaul):
  if Backhaul:
    o = Destination
    d = Origin
  else:
    o = Origin
    d = Destination
  json_data = {
    'origin': {
        'address': o,
    },
    'destination': {
        'address': d,
    },
    'travelMode': 'DRIVE',
    'routingPreference': 'TRAFFIC_UNAWARE',
#    'departureTime': '2023-10-15T15:01:23.045123456Z',
    'computeAlternativeRoutes': False,
    'routeModifiers': {
        'avoidTolls': False,
        'avoidHighways': False,
        'avoidFerries': True,
    },
    'languageCode': 'en-US',
  }

  data = response = requests.post('https://routes.googleapis.com/directions/v2:computeRoutes', headers=headers, json=json_data).json()
  return polyline.decode(data['routes'][0]['polyline']['encodedPolyline'])

def createSimpleRouteWithWaypointInjection(o, d, w_s, w_e):
  json_data = {
    'origin': {
        'address': o,
    },
    'destination': {
        'address': d,
    },
    "intermediates": [
    {
      "address": w_s,
    },
    {
      "address": w_e,
    }
  ],
    'travelMode': 'DRIVE',
    'routingPreference': 'TRAFFIC_UNAWARE',
#    'departureTime': '2023-10-15T15:01:23.045123456Z',
    'computeAlternativeRoutes': False,
    'routeModifiers': {
        'avoidTolls': False,
        'avoidHighways': False,
        'avoidFerries': True,
    },
    'languageCode': 'en-US',
  }

  data = response = requests.post('https://routes.googleapis.com/directions/v2:computeRoutes', headers=headers, json=json_data)
  return polyline.decode(data.json()['routes'][0]['polyline']['encodedPolyline'])

def calculateCO2(Origin, Destination, Backhaul, Tonnage):
  if Backhaul:
    o = Destination
    d = Origin
  else:
    o = Origin
    d = Destination
  json_data = {
    'origin': {
        'address': o,
    },
    'destination': {
        'address': d,
    },
    'travelMode': 'DRIVE',
    'routingPreference': 'TRAFFIC_UNAWARE',
#    'departureTime': '2023-10-15T15:01:23.045123456Z',
    'computeAlternativeRoutes': False,
    'routeModifiers': {
        'avoidTolls': False,
        'avoidHighways': False,
        'avoidFerries': True,
    },
    'languageCode': 'en-US',
  }

  data = response = requests.post('https://routes.googleapis.com/directions/v2:computeRoutes', headers=headers, json=json_data).json()
  distance = data['routes'][0]['distanceMeters']
  calc_to_ret = (0.1*int(Tonnage)*distance)/1000
  return str(round(calc_to_ret))

def calculateCO2Waypoints(o, d, w_s, w_e, tonnage):
  json_data = {
    'origin': {
        'address': o,
    },
    'destination': {
        'address': d,
    },
    "intermediates": [
    {
      "address": w_s,
    },
    {
      "address": w_e,
    }
  ],
    'travelMode': 'DRIVE',
    'routingPreference': 'TRAFFIC_UNAWARE',
#    'departureTime': '2023-10-15T15:01:23.045123456Z',
    'computeAlternativeRoutes': False,
    'routeModifiers': {
        'avoidTolls': False,
        'avoidHighways': False,
        'avoidFerries': True,
    },
    'languageCode': 'en-US',
  }

  data = response = requests.post('https://routes.googleapis.com/directions/v2:computeRoutes', headers=headers, json=json_data)
  distance = data.json()['routes'][0]['distanceMeters']
  calc_to_ret = (0.066*int(tonnage)*distance)/1000
  return str(round(calc_to_ret))

app.layout = html.Div([
    html.H1(id = 'textout'),
    html.Div(id='output-state'),
    dcc.Dropdown(
        id = 'dropdown-to-show_or_hide-element',
        options=[
            {'label': 'Logged in as: Construction company', 'value': 'con-com'},{'label': 'Loggind in as: Client', 'value': 'client'}
            ],value = 'con-com', persistence=False),
    html.Div([
    html.Br(),
    html.Br(),
    dcc.Input(id = 'o', value = 'Av Desarrollo 1801, Complejo Industrial Impulso, 31183 Chihuahua, Chih., Mexico', type = 'text', persistence=False),
    dcc.Input(id = 'd', value = 'Blvd. Adolfo López Mateos 909 Ote. Esq. con, Av Tamaulipas, Valle de Aguayo, 87020 Cd Victoria, Tamps., Mexico', type = 'text', persistence=False),
    dcc.Input(id = 'tonnage', value = 32, type = 'number', persistence=False),
    html.Button('Register', id='btn-nclicks-1', n_clicks=0),
    ], id="element-to-hide"),
    html.Br(),
    html.Br(),
    dcc.Input(id = 'w_s', value = '67806 Linares, Nuevo Leon, Mexico', type = 'text'),
    dcc.Input(id = 'w_e', value = 'Blvd Harold R. Pape 1202, La Loma, 25770 Monclova, Coah., Mexico', type = 'text', persistence=False),
    dcc.Input(id = 'tonnage2', value = 15, type = 'number', persistence=False),
    html.Button('Suggest', id='btn-nclicks-2', n_clicks=0)
])

@app.callback(Output('output-state', 'children'),
              Input('btn-nclicks-1', 'n_clicks'),
              Input('btn-nclicks-2', 'n_clicks'),
              State('o', 'value'),
              State('d', 'value'),
              State('w_s', 'value'),
              State('w_e', 'value'),
              State('tonnage', 'value'),
              State('tonnage2', 'value'))
def update_output(btn1, btn2, o, d, w_s, w_e, tonnage, tonnage2):
  if "btn-nclicks-1" == ctx.triggered_id:
    fig_map1 = go.Figure()
    df = pd.DataFrame(createSimpleRoute(o, d, False), columns =['x', 'y'])
    df_b = pd.DataFrame(createSimpleRoute(o, d, True), columns =['x', 'y'])
    co2_1 = calculateCO2(o, d, False, tonnage)
    co2_2 = calculateCO2(o, d , True, 1)
    fig_map1.add_trace((go.Scattermapbox(name="Planned Itinerary (" + co2_1 + " kg CO2)", mode = "lines", lat = df["x"].tolist(), lon = df["y"].tolist(), marker=go.scattermapbox.Marker(color='blue'))))
    fig_map1.add_trace((go.Scattermapbox(name="Empty truck (" + co2_2 + " kg CO2)", mode = "lines", lat = df_b["x"].tolist(), lon = df_b["y"].tolist(), marker=go.scattermapbox.Marker(color='red'))))

    fig_map1.update_layout(margin ={'l':10,'t':10,'b':10,'r':10}, mapbox = {'center': {'lon': -100, 'lat': 25.5}, 'style': "open-street-map", 'zoom': 6},height=700)
    return dcc.Graph(figure=fig_map1, id='map'), html.Br(), html.Br()

  if "btn-nclicks-2" == ctx.triggered_id:
    fig_map1 = go.Figure()
    df_b2 = pd.DataFrame(createSimpleRouteWithWaypointInjection(o, d, w_s, w_e), columns=['x', 'y'])
    df = pd.DataFrame(createSimpleRoute(o, d, False), columns =['x', 'y'])
    df_b = pd.DataFrame(createSimpleRoute(o, d, True), columns =['x', 'y'])
    co2_1 = calculateCO2(o, d, False, tonnage)
    co2_2 = calculateCO2(o, d , True, 1)
    fig_map1.add_trace((go.Scattermapbox(name="Planned Itinerary (" + co2_1 + " kg CO2)", mode = "lines", lat = df["x"].tolist(), lon = df["y"].tolist(), marker=go.scattermapbox.Marker(color='blue'))))
    fig_map1.add_trace((go.Scattermapbox(name="Empty truck (" + co2_2 + " kg CO2)", mode = "lines", lat = df_b["x"].tolist(), lon = df_b["y"].tolist(), marker=go.scattermapbox.Marker(color='red'))))

    co2_3 = calculateCO2Waypoints(o, d, w_s, w_e, tonnage2)

    fig_map1.add_trace((go.Scattermapbox(name="Suggest Path (" + co2_3 + " kg CO2)", mode = "lines", lat = df_b2["x"].tolist(), lon = df_b2["y"].tolist(), marker=go.scattermapbox.Marker(color='green'))))
    
    fig_map1.update_layout(margin ={'l':10,'t':10,'b':10,'r':10}, mapbox = {'center': {'lon': -100, 'lat': 25.5}, 'style': "open-street-map", 'zoom': 6},height=700)
    return dcc.Graph(figure=fig_map1, id='map'), html.Br(), html.Br()

@app.callback(Output(component_id='element-to-hide', component_property='style'), [Input(component_id='dropdown-to-show_or_hide-element', component_property='value')])
def show_hide_element(visibility_state):
  if visibility_state == 'con-com':
    return {'display': 'block'}
  if visibility_state == 'client':
    return {'display': 'none'}

if __name__ == "__main__":
    app.run_server(debug=True, threaded=True)