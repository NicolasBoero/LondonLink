import pandas as pd
import geopandas as gpd
import requests
import folium
import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from folium.plugins import Fullscreen, BeautifyIcon
from geopy.geocoders import Nominatim
import geopy.distance
from folium.plugins import MarkerCluster
import datetime


# STYLE -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


st.set_page_config(layout="wide", page_title='LondonLink', page_icon = 'LondonLink.jpg')

def folium_static(fig, width=1100, height=790):
    if isinstance(fig, folium.Map):
        fig = folium.Figure().add_child(fig)
        return components.html(
            fig.render(), height=(fig.height or height) + 10, width=width)

st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 3rem;
                    padding-left: 0rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)


# CSV -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


polygons = gpd.read_file('polygonz.json')
congestion_charge = polygons[polygons['name'] == 'London Congestion Charge Zone'][['geometry']]
london_borders = polygons[polygons['name'] == 'London Low Emission Zone'][['geometry']]
carpark = pd.read_csv('car_park.csv')
charge = pd.read_csv('charge.csv')
bikes = pd.read_csv('bikes.csv')
metro = pd.read_csv('metro.csv')


p = {'gray': [[51.619839, -0.303266], [51.607701, -0.294693], [51.594188, -0.286219], [51.584845, -0.27879], [51.563198, -0.279262], [51.553986, -0.249837], [51.551955, -0.239068], [51.549146, -0.221537], [51.547183, -0.204248], [51.547533, -0.191357], [51.546825, -0.179845], [51.543681, -0.174894], [51.513362, -0.148795], [51.506947, -0.142787], [51.501603, -0.125984], [51.50427, -0.105331], [51.505881, -0.086807], [51.49775, -0.063993],[51.498053,-0.049667], [51.503734, -0.019121], [51.500474, 0.004295], [51.514029, 0.008025], [51.528178, 0.004997], [51.541508, -0.00241]], 
     'darkblue': [[[51.65152, -0.149171], [51.647726, -0.132182], [51.632315, -0.127816], [51.616446, -0.133062], [51.607034, -0.124235], [51.597479, -0.109886], [51.590272, -0.102953], [51.570738, -0.096118], [51.564778, -0.105876], [51.558655, -0.107457], [51.552697, -0.113244], [51.548519, -0.118493], [51.531683, -0.123538], [51.523073, -0.124285], [51.51758, -0.120475], [51.513093, -0.124436], [51.511386, -0.128426], [51.51005, -0.133798], [51.506947, -0.142787], [51.503035, -0.152441], [51.501669, -0.160508], [51.494094, -0.174138], [51.494316, -0.182658], [51.492063, -0.193378], [51.490311, -0.213427], [51.503057, -0.280462], [51.501003, -0.307424], [51.499319, -0.314719],[51.495635, -0.324939], [51.481274, -0.352224], [51.473213, -0.356474], [51.471295, -0.366578], [51.473469, -0.386544], [51.466747, -0.423191], [51.471618, -0.454037]], [[51.503057, -0.280462], [51.51014, -0.288265], [51.517505, -0.288868], [51.527123, -0.284341], [51.540627, -0.29961], [51.550815, -0.315745], [51.556946, -0.336435], [51.564888, -0.352492], [51.575147, -0.371127], [51.576506, -0.397373], [51.573202, -0.412973], [51.571354, -0.421898], [51.56177, -0.442225], [51.553715, -0.449828], [51.546565, -0.477949]]], 
     'green': [[[51.558659, 0.250855], [51.55856, 0.235809], [51.554093, 0.219116], [51.549775, 0.19864], [51.544096, 0.166017], [51.541639, 0.147527], [51.540331, 0.127016], [51.538372, 0.10153], [51.539413, 0.080988], [51.538948, 0.051186], [51.53534, 0.035263], [51.531341, 0.017451], [51.528178, 0.004997], [51.524839, -0.011538], [51.52694, -0.025128], [51.525122, -0.03364], [51.521858, -0.046596], [51.519498, -0.059858], [51.515037, -0.072384], [51.509971, -0.076546], [51.5107, -0.085969], [51.511451, -0.090357], [51.512117, -0.094009], [51.509613, -0.104166], [51.511006, -0.11426], [51.507058, -0.122666], [51.501603, -0.125984], [51.499544, -0.133608], [51.495812, -0.143826], [51.49227, -0.156377], [51.494094, -0.174138], [51.494316, -0.182658], [51.490459, -0.206636], [51.490311, -0.213427], [51.494122, -0.235881], [51.494917, -0.245704], [51.495148, -0.254555], [51.494627, -0.267972], [51.503057, -0.280462], [51.51014, -0.288265], [51.514993, -0.302131]], [[51.463152, -0.301448], [51.477069, -0.285148], [51.491745, -0.275276], [51.495148, -0.254555]], [[51.496156, -0.210502], [51.492063, -0.193378]], [[51.421505, -0.206444], [51.434573, -0.199719], [51.434573, -0.199719], [51.445073, -0.206602], [51.459205, -0.211], [51.468262, -0.208731], [51.475277, -0.20117], [51.480081, -0.195422], [51.487168, -0.195593], [51.492063, -0.193378], [51.501055, -0.192792], [51.509128, -0.196104], [51.512284, -0.187938], [51.516981, -0.17616]]], 
     'red': [[[51.569721, -0.437816], [51.560736, -0.41071], [51.556893, -0.399076], [51.548236, -0.368699], [51.542657, -0.345789], [51.536717, -0.323446], [51.530177, -0.292704], [51.523524, -0.259755], [51.516612, -0.247248], [51.511959, -0.224297], [51.504791, -0.219213], [51.507143, -0.205679], [51.509128, -0.196104], [51.510312, -0.187152], [51.511723, -0.175494], [51.513424, -0.158953], [51.513362, -0.148795], [51.515224, -0.141903], [51.516018, -0.130888], [51.51758, -0.120475], [51.518247, -0.111583], [51.514936, -0.097567], [51.513395, -0.089095], [51.51794, -0.083162], [51.527222, -0.055506], [51.525122, -0.03364], [51.541508, -0.00241], [51.556589, -0.005523], [51.568324, 0.008194], [51.580678, 0.02144], [51.591907, 0.027338], [51.606899, 0.03397], [51.626605, 0.046757], [51.641443, 0.055476], [51.645386, 0.083782], [51.671759, 0.103085], [51.69368, 0.113767]], [[51.514993, -0.302131], [51.518001, -0.28098], [51.523524, -0.259755]], [[51.568324, 0.008194], [51.575501, 0.028527], [51.576243, 0.04536], [51.576544, 0.066185], [51.575726, 0.090004], [51.585689, 0.088585], [51.595618, 0.091004], [51.603659, 0.093482], [51.613378, 0.092066], [51.617916, 0.075041], [51.617199, 0.043647], [51.606899, 0.03397]]], 
     'blue': [[51.462961, -0.114531], [51.472184, -0.122644], [51.485739, -0.123303], [51.489097, -0.133761], [51.495812, -0.143826], [51.506947, -0.142787], [51.515224, -0.141903], [51.524951, -0.138321], [51.531683, -0.123538], [51.546269, -0.103538], [51.564778, -0.105876], [51.582931, -0.073306], [51.588315, -0.06024], [51.586768, -0.041185], [51.582948, -0.019842]], 
     'pink': [[51.539413, 0.080988], [51.538948, 0.051186], [51.53534, 0.035263], [51.531341, 0.017451], [51.528178, 0.004997], [51.524839, -0.011538], [51.52694, -0.025128], [51.525122, -0.03364], [51.521858, -0.046596], [51.519498, -0.059858], [51.515037, -0.072384], [51.51794, -0.083162], [51.518338, -0.088627], [51.520275, -0.097993], [51.520214, -0.105054], [51.531683, -0.123538], [51.525604, -0.135829], [51.52384, -0.144262], [51.522883, -0.15713], [51.519858, -0.167832], [51.516981, -0.17616], [51.519113, -0.188748], [51.52111, -0.201065], [51.517449, -0.210391], [51.513389, -0.217799], [51.502005, -0.226715], [51.505579, -0.226375], [51.509669, -0.22453]], 
     'yellow': [[51.509128, -0.196104], [51.512284, -0.187938], [51.516981, -0.17616], [51.522883, -0.15713], [51.52384, -0.144262], [51.525604, -0.135829], [51.531683, -0.123538], [51.520214, -0.105054], [51.520275, -0.097993], [51.518338, -0.088627], [51.51794, -0.083162], [51.509971, -0.076546], [51.5107, -0.085969], [51.511451, -0.090357], [51.512117, -0.094009], [51.509613, -0.104166], [51.511006, -0.11426], [51.507058, -0.122666], [51.501603, -0.125984], [51.495812, -0.143826], [51.494094, -0.174138], [51.494316, -0.182658], [51.501055, -0.192792], [51.509128, -0.196104]], 
     'orange': [[51.494505, -0.099185], [51.498808, -0.112315], [51.504269, -0.113356], [51.507058, -0.122666], [51.507819, -0.126137], [51.51005, -0.133798], [51.515224, -0.141903], [51.523344, -0.146444], [51.521602, -0.163013], [51.520299, -0.17015], [51.523263, -0.183783], [51.529777, -0.185758], [51.534979, -0.194232], [51.534443, -0.204882], [51.530545, -0.22505], [51.536305, -0.257774], [51.544041, -0.275859], [51.55232, -0.296642], [51.56258, -0.303992], [51.570229, -0.308448], [51.581786, -0.316946], [51.592216, -0.334896]], 
     'darkred': [[[51.514246, -0.075689], [51.51794, -0.083162], [51.518338, -0.088627], [51.520275, -0.097993], [51.520214, -0.105054], [51.531683, -0.123538], [51.525604, -0.135829], [51.52384, -0.144262], [51.546825, -0.179845], [51.563198, -0.279262], [51.571972, -0.295107], [51.578481, -0.318056], [51.579197, -0.337226], [51.584872, -0.362408], [51.592901, -0.381161], [51.600572, -0.409464], [51.611053, -0.423829], [51.629845, -0.432454], [51.640247, -0.473273], [51.654249, -0.518312], [51.668109, -0.560519], [51.674207, -0.60759]], [[51.705208, -0.611247], [51.668109, -0.560519]], [[51.657446, -0.417377], [51.647044, -0.441718], [51.629845, -0.432454]], [[51.546565, -0.477949], [51.553715, -0.449828], [51.56177, -0.442225], [51.571354, -0.421898], [51.573202, -0.412973], [51.576506, -0.397373], [51.575147, -0.371127], [51.57971, -0.3534], [51.579197, -0.337226]]], 
     'black': [[[51.402142, -0.194839],[51.415309, -0.192005],[51.41816, -0.178086],[51.42763,-0.168374],[51.435678,-0.159736],[51.443259, -0.152707],[51.452654,-0.147582], [51.461742, -0.138317], [51.465135, -0.130016], [51.472184, -0.122644], [51.48185, -0.112439], [51.488337, -0.105963], [51.494505, -0.099185], [51.501199, -0.09337], [51.505881, -0.086807], [51.518338, -0.088627], [51.526065, -0.088193], [51.532624, -0.105898],  [51.531683, -0.12353], [51.527365, -0.132754], [51.539292, -0.14274], [51.550409, -0.140545], [51.556822, -0.138433], [51.565478, -0.134819], [51.577532, -0.145857], [51.587131, -0.165012], [51.600921, -0.192527], [51.609426, -0.188362], [51.618014, -0.18542], [51.630597, -0.17921], [51.650541, -0.194298]], [[51.608229, -0.209986], [51.600921, -0.192527]], [[51.613653, -0.274928], [51.602774, -0.264048], [51.595424, -0.249919], [51.583301, -0.226424], [51.57665, -0.213622], [51.572259, -0.194039], [51.556239, -0.177464], [51.550529, -0.164783], [51.544118, -0.153388], [51.534679, -0.138789], [51.527365, -0.132754], [51.524951, -0.138321], [51.520599, -0.134361], [51.516018, -0.130888], [51.511386, -0.128426], [51.507819, -0.126137], [51.507058, -0.122666], [51.504269, -0.113356], [51.488337, -0.105963]], [[51.488337, -0.105963], [51.479912, -0.128476], [51.479932, -0.142142]]]}


# SIDEBAR ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

with st.sidebar:
    navbar_options = option_menu(
        menu_title=None,
        options=["", " ", "  ", "T", "P"],
        icons=['house',"bicycle", 'plug', "T", " "],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

start_address = st.sidebar.text_input('From:')
finish_address = st.sidebar.text_input('To:')
    
type = st.sidebar.radio(
     "What's your type of car:",
     ('Gas Car', 'Electric Car'))

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

map = folium.Map(location = [51.502, -0.12] , zoom_start =10, control_scale = True)
marker_cluster = MarkerCluster().add_to(map)
geolocator = Nominatim(user_agent="app.py")


folium.GeoJson(london_borders, style_function=lambda x: {'fillColor': '#5296E6', 
                                                        'color': '#004698',
                                                        'weight': '1.5'}
    ).add_to(map)

folium.GeoJson(congestion_charge, style_function=lambda x: {'fillColor': '', 
                                            'color': '#E84B4B',
                                            'weight': '2'}
    ).add_to(map)


# NAVBAR ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def navbar(navbar_options):
    if navbar_options == 'T':

        # for index, row in metro.iterrows():
        #     link = f"https://api.tfl.gov.uk/StopPoint/{row['naptanID']}/Crowding/{row['urlLines']}?direction=inbound"
        #     r = requests.get(link).json()
        #     for i in range(100):
        #         try:
        #             crowding = pd.json_normalize(data=r['lines'][i]['crowding']['passengerFlows'])
        #             crowding = crowding.groupby(['timeSlice']).agg({'value': 'mean'}).sort_values(by='value', ascending=False).reset_index()
        #         except:
        #             pass

        # crowding[['start', 'finish']] = crowding['timeSlice'].str.split('-', expand=True)
        # crowding['start'] = crowding['start'].apply(lambda x: x[:2] + ':' + x[2:])
        # crowding['finish'] = crowding['finish'].apply(lambda x: x[:2] + ':' + x[2:])
        # crowding['start'] = pd.to_datetime(crowding['start'])
        # crowding['finish'] = pd.to_datetime(crowding['finish'])
        # now = datetime.datetime.now()  

        # for index, row in crowding.iterrows():
        #     if row['start'] < now <= row['finish']:
        #         avg_crowd = row['value']


        for key, value in p.items():
            all_lines = folium.PolyLine(
            value,
            color = key,
            ).add_to(map)

        for index, row in metro.iterrows():
            all_stations = folium.CircleMarker(
                location = (row['lat'], row['lon']),
                tooltip = row['Name'],
                fill_opacity = 1,
                color = 'beige',
                fill_color = 'white', 
                radius = 1
            ).add_to(map)
        
        return all_stations, all_lines,

    elif navbar_options == " ":

        for index, row in bikes.iterrows():
            all_bike_points = folium.Marker(
                location = (row['latitude'], row['longitude']),
                tooltip = ("Station : {name}<br>"
                           "Available bikes : {bikes}<br>"
                           "Available docks : {docks}<br>"
                          ).format(name=row['commonName'],
                                   bikes=row['NbBikes'],
                                   docks=row['EmptyDocks']),
                icon = folium.features.CustomIcon('bikeR1.webp', icon_size=(25, 25))
            ).add_to(marker_cluster)

        return all_bike_points

    elif navbar_options == "  ":

        for index, row in charge.iterrows():
            all_connectors = folium.Marker(
                location = (row['latitude'], row['longitude']),
                tooltip = ("Station : {name}<br>"
                           "Available : {available}<br>"
                           "Charging : {charging}<br>"
                          ).format(name=row['Name'],
                                   available=row['Available'],
                                   charging=row['Charging']),
                icon = folium.features.CustomIcon('plug.webp', icon_size=(15, 15))
            ).add_to(map)

        return all_connectors

    elif navbar_options == 'P':
        
        for index, row in carpark.iterrows():
            all_carparks = folium.Marker(
                location = (row['lat'], row['lon']),
                tooltip = ("{name}<br>"
                           "Available : {free}<br>"
                           "Occupied : {occupied}<br>"
                          ).format(name=row['name'],
                                   free=row['free'],
                                   occupied=row['occupied']),
                icon = folium.features.CustomIcon('ParkR.svg.png', icon_size=(16, 17))
            ).add_to(map)

        return all_carparks


navbar(navbar_options)


# JOURNEY ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def journey(start_address, finish_address, type):
    while True:
        try:
            start_coordinates = geolocator.geocode(f"{start_address}")
            start = (start_coordinates.latitude, start_coordinates.longitude)
            start_marker = folium.Marker(
                location=start,
                icon = folium.Icon(color='blue', prefix = 'fa', icon='home'),
                tooltip = start_address
                ).add_to(map)

            finish_coordinates  = geolocator.geocode(f"{finish_address}")
            finish = (finish_coordinates.latitude, finish_coordinates.longitude)
            finish_marker = folium.Marker(
                location=finish,
                icon = folium.Icon(color='blue', prefix = 'fa', icon='flag'),
                tooltip = finish_address
                ).add_to(map)

            if type == 'Electric Car':
                charge["coordinates"] = charge[["latitude","longitude"]].apply(list, axis=1)
                charge["distance-arr"] = charge["coordinates"].apply(lambda x: x.append(geopy.distance.geodesic(finish, x).km))
                charge['distance-arr'] = charge['coordinates'].str[-1]
                charge['coordinates'] = charge['coordinates'].apply(lambda x: x[:-1])
                charge["distance-dep"] = charge["coordinates"].apply(lambda x: x.append(geopy.distance.geodesic(start, x).km))
                charge['distance-dep'] = charge['coordinates'].str[-1]
                charge['coordinates'] = charge['coordinates'].apply(lambda x: x[:-1])

                
                # for index, row in charge.iterrows():
                #     all_charges = folium.Marker(
                #         location = (row['latitude'], row['longitude']),
                #         tooltip = ("Station : {name}<br>"
                #            "Available : {available}<br>"
                #            "Charging : {charging}<br>"
                #           ).format(name=row['Name'],
                #                    available=row['Available'],
                #                    charging=row['Charging']),
                #         icon = folium.features.CustomIcon('plug.webp', icon_size=(20, 20))
                #     ).add_to(map)

                charges_available = charge[charge['Available'] !=0]

                best_charge = folium.Marker(
                    location = (charges_available.loc[charges_available['distance-arr'] == charges_available['distance-arr'].min(), 'coordinates'].iloc[0]),
                    icon = folium.Icon(color='darkblue', prefix = 'fa', icon='plug', size = 0.5)
                    ).add_to(map)

                st.sidebar.markdown(f"**Fastest route** : {round(charges_available.loc[charges_available['distance-arr'] == charges_available['distance-arr'].min(), 'distance-dep'].iloc[0], 2)} KM")
                st.sidebar.markdown(f"**Recommanded charging station** : {charges_available.loc[charges_available['distance-arr'] == charges_available['distance-arr'].min(), 'Name'].iloc[0]}")
                st.sidebar.markdown(f"**Charging point available** : {charges_available.loc[charges_available['distance-arr'] == charges_available['distance-arr'].min(), 'Available'].iloc[0]}")
                st.sidebar.markdown(f"**Walk to destination** : {round(charges_available['distance-arr'].min(), 2)} KM")

                return best_charge, charges_available

            elif type == 'Gas Car':

                # DISTANCE FINISH - CARPARK
                carpark1 = carpark.groupby('name').agg({'bayCount': 'sum', 'free':'sum', 'occupied': 'sum', 'lat': 'first', 'lon': 'first'}).reset_index()
                carpark1["coordinates"] = carpark1[["lat","lon"]].apply(list, axis=1)
                carpark1["distance-arr"] = carpark1["coordinates"].apply(lambda x: x.append(geopy.distance.geodesic(finish, x).km))
                carpark1['distance-arr'] = carpark1['coordinates'].str[-1]
                carpark1['coordinates'] = carpark1['coordinates'].apply(lambda x: x[:-1])

                # DISTANCE START - CARPARK
                carpark1["distance-dep"] = carpark1["coordinates"].apply(lambda x: x.append(geopy.distance.geodesic(start, x).km))
                carpark1['distance-dep'] = carpark1['coordinates'].str[-1]
                carpark1['coordinates'] = carpark1['coordinates'].apply(lambda x: x[:-1]) 

                # DISTANCE DELTA
                carpark1['delta_distance'] = carpark1['distance-arr'] + carpark1['distance-dep']
                carpark1['algo'] = carpark1['delta_distance'] + carpark1['distance-arr']

                # for index, row in carpark1.iterrows():
                #     all_carparks =  folium.Marker(
                #         location = (row['lat'], row['lon']),
                #         tooltip = ("{name}<br>"
                #            "Available : {free}<br>"
                #            "Occupied : {occupied}<br>"
                #           ).format(name=row['name'],
                #                    free=row['free'],
                #                    occupied=row['occupied']),
                #         icon = folium.features.CustomIcon('ParkR.svg.png', icon_size=(16, 17))
                #     ).add_to(map)

                best_carpark = folium.Marker(
                    location = carpark1.loc[carpark1['algo'] == carpark1['algo'].min(), 'coordinates'].iloc[0],
                    tooltip = ("{name}<br>"
                           "Available : {free}<br>"
                           "Occupied : {occupied}<br>"
                          ).format(name=carpark1.loc[carpark1['algo'] == carpark1['algo'].min(), 'name'].iloc[0],
                                   free=carpark1.loc[carpark1['algo'] == carpark1['algo'].min(), 'free'].iloc[0],
                                   occupied=carpark1.loc[carpark1['algo'] == carpark1['algo'].min(), 'occupied'].iloc[0]),
                    icon = folium.Icon(color='red', prefix = 'fa', icon='car')
                ).add_to(map)


                # DISTANCE CAR PARK - METRO

                z = carpark1.loc[carpark1['algo'] == carpark1['algo'].min(), 'coordinates'].iloc[0]
                metro["coordinates"] =  metro[["lat","lon"]].apply(list, axis=1)
                metro["distance"] = metro["coordinates"].apply(lambda x: x.append(geopy.distance.geodesic(z, x).km))
                metro['distance'] = metro['coordinates'].str[-1]
                metro['coordinates'] = metro['coordinates'].apply(lambda x: x[:-1])
                line = metro.loc[metro['distance'] == metro['distance'].min(), 'colors'].iloc[0]

                # DISTANCE METRO - ARR

                d = metro[metro['colors'] == line]
                d = d.drop(columns='distance')
                d["distance"] = d['coordinates'].apply(lambda x: x.append(geopy.distance.geodesic(finish, x).km))
                d['distance'] = d['coordinates'].str[-1]
                d['coordinates'] = d['coordinates'].apply(lambda x: x[:-1])

                # CROWDING
 
                link = f"https://api.tfl.gov.uk/StopPoint/{metro.loc[metro['distance'] == metro['distance'].min(), 'naptanID'].iloc[0]}/Crowding/{(d.loc[d['distance'] == d['distance'].min(), 'urlLines'].iloc[0])}?direction=inbound"
                r = requests.get(link).json()
                for i in range(100):
                    try:
                        crowding = pd.json_normalize(data=r['lines'][i]['crowding']['passengerFlows'])
                        crowding = crowding.groupby(['timeSlice']).agg({'value': 'mean'}).sort_values(by='value', ascending=False).reset_index()
                    except:
                        pass

                crowding[['start', 'finish']] = crowding['timeSlice'].str.split('-', expand=True)
                crowding['start'] = crowding['start'].apply(lambda x: x[:2] + ':' + x[2:])
                crowding['finish'] = crowding['finish'].apply(lambda x: x[:2] + ':' + x[2:])
                crowding['start'] = pd.to_datetime(crowding['start'])
                crowding['finish'] = pd.to_datetime(crowding['finish'])

                now = datetime.datetime.now()  

                for index, row in crowding.iterrows():
                    if row['start'] < now <= row['finish']:
                        avg_crowd = row['value']
                    

                # POPUP STATION

                station_marker = folium.Marker(
                    location = d.loc[d['distance'] == d['distance'].min(), 'coordinates'].iloc[0],
                    tooltip = d.loc[d['distance'] == d['distance'].min(), 'Name'].iloc[0], 
                    icon = folium.Icon(color='green', prefix = 'fa', icon='location-arrow', size = 0.5),       
                ).add_to(map)

                d = d.drop(columns='Unnamed: 0')  


                # POPUP LINE

                line_marker = folium.PolyLine(
                    p[f"{metro.loc[metro['distance'] == metro['distance'].min(), 'colors'].iloc[0]}"],
                    color = metro.loc[metro['distance'] == metro['distance'].min(), 'colors'].iloc[0],
                    ).add_to(map)


                stop_points = metro[metro['colors'] == metro.loc[metro['distance'] == metro['distance'].min(), 'colors'].iloc[0]]

                for index, row in stop_points.iterrows():
                    stop_points_marker = folium.CircleMarker(
                        location = (row['lat'], row['lon']),
                        tooltip = row['Name'],
                        fill_opacity = 1,
                        color = 'grey',
                        fill_color = 'white', 
                        radius = 4,
                        tileSize = 1
                    ).add_to(map)

                st.sidebar.markdown(f"**Recommanded car park**: {carpark1.loc[carpark1['algo'] == carpark1['algo'].min(), 'name'].iloc[0]}")
                st.sidebar.markdown(f"**Distance** : {round(carpark1.loc[carpark1['algo'] == carpark1['algo'].min(), 'distance-dep'].iloc[0], 2)} KM")
                st.sidebar.markdown(f"**Parking spots available** : {carpark1.loc[carpark1['algo'] == carpark1['algo'].min(), 'free'].iloc[0]}")
                st.sidebar.subheader(f"Recommanded route : ")
                st.sidebar.write(f"**Tube** : {metro.loc[metro['distance'] == metro['distance'].min(), 'Name'].iloc[0]} to {d.loc[d['distance'] == d['distance'].min(), 'Name'].iloc[0]}, {metro.loc[metro['distance'] == metro['distance'].min(), 'Line'].iloc[0]} Line" )
                
                crowding_level = ""
                if avg_crowd <=50: 
                    crowding_level = "  (not busy)"
                elif avg_crowd>50 and avg_crowd<=100:
                    crowding_level = "  (little busy)"
                elif avg_crowd>100:
                    crowding_level = "  (too busy)"
                
                st.sidebar.markdown(f"Crowding : {avg_crowd} {crowding_level}")
                st.sidebar.markdown(f"**Walk to destination** : {round(d['distance'].min(), 2)} KM")

                return best_carpark, start_marker, finish_marker, station_marker, line_marker, charge, stop_points
                    
        except AttributeError:
            return map

journey(start_address, finish_address, type)

folium_static(map)
