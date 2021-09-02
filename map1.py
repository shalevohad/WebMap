import os
import time
import folium
import requests
import pandas
from pandas.core.indexes.base import Index

centeralMapCoordination = [31.704696116237855, 34.95518761019271]
# mapTiles = "Stamen Terrain"
mapTiles = "OpenStreetMap"


def downloadExternalFile(url, filename):
    myfile = requests.get(url)
    open(filename, 'wb').write(myfile.content)


# Generating the map instance
map = folium.Map(location=centeralMapCoordination,
                 zoom_start=6, tiles=mapTiles)

# Population
PopulationFilepath = 'world.json'
if (os.path.exists(PopulationFilepath)):
    def population_color_producer(population):
        if population < 10000000:
            return 'green'
        elif 10000000 <= population < 200000000:
            return 'orange'
        else:
            return 'red'

    fgp = folium.FeatureGroup(name="Population")
    fgp.add_child(
        folium.GeoJson(
            data=open('world.json', 'r', encoding='utf-8-sig').read(),
            style_function=lambda x: {
                'fillColor': population_color_producer(x['properties']['POP2005'])}
        )
    )

    map.add_child(fgp)

# USA Volcanoes
GroupName = "USA Volcanoes"
VolcanoesFilepath = 'Volcanoes.txt'
if (os.path.exists(VolcanoesFilepath)):
    def color_producer(elevation):
        if elevation < 1000:
            return 'green'
        elif 1000 <= elevation < 3000:
            return 'orange'
        else:
            return 'red'

    data = pandas.read_csv(VolcanoesFilepath)
    html = """<h4>Volcano information:</h4>
    <strong>Name:</strong> <a href="https://www.google.com/search?q=%%22%s%%22" target="_blank">%s</a><br>
    <strong>Height:</strong> %.1f m<br>
    <strong>Status:</strong> %s
    """

    fgv = folium.FeatureGroup(name=GroupName, show=False)
    for i in data.index:
        innerData = dict(data.iloc[i, :])
        iframe = folium.IFrame(
            html=html % (innerData["NAME"], innerData["NAME"],
                         innerData["ELEV"], innerData["STATUS"]),
            width=200,
            height=150)

        fgv.add_child(
            folium.CircleMarker(
                location=[innerData["LAT"], innerData["LON"]],
                popup=folium.Popup(iframe, parse_html=True),
                color="gray",
                fill_color=color_producer(innerData["ELEV"]),
                fill=True,
                fill_opacity=0.7,
                radius=12
            )
        )

    map.add_child(fgv)

# Asia fires
GroupName = "Fire's in Russia and Asia (24hr)"
WFfileUrl = "https://firms2.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Russia_Asia_24h.csv"
WFfilePath = 'WFIsrael.csv'
WFconfidance = 70
if(os.path.exists(WFfilePath) == False or os.path.getctime(WFfilePath) <= int(time.time())-86400):
    downloadExternalFile(WFfileUrl, WFfilePath)

if(os.path.exists(WFfilePath)):
    dataWF = pandas.read_csv(WFfilePath)
    dataWF = dataWF[dataWF['confidence'] > WFconfidance]
    dataWF["daynight"] = dataWF["daynight"].apply(
        lambda x: "Night" if x == "N" else "Day")
    html = """<h4>Fire information:</h4>
    <strong>Date:</strong>%s %.0f<br>
    <strong>Lat/Lon:</strong>%s / %s<br>
    <strong>confidence:</strong> %s<br>
    <strong>daynight:</strong> %s
    """

    fgwf = folium.FeatureGroup(name=GroupName)
    for i in range(len(dataWF)):
        innerWFData = dict(dataWF.iloc[i, :])
        iframe = folium.IFrame(
            html=html % (innerWFData["acq_date"], innerWFData["acq_time"],
                         innerWFData["latitude"], innerWFData["longitude"],
                         innerWFData["confidence"],
                         innerWFData["daynight"]),

            width=200,
            height=150)

        fgwf.add_child(
            folium.Marker(
                location=[innerWFData["latitude"], innerWFData["longitude"]],
                popup=folium.Popup(iframe, parse_html=True),
                icon=folium.Icon(color='red', prefix='fa',
                                 icon="fire-extinguisher")
            )
        )

    map.add_child(fgwf)

# Map
map.add_child(folium.LayerControl())

map.save("Map.html")
