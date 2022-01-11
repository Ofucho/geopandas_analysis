from shapely.geometry import Polygon, LineString, MultiPolygon, MultiLineString
import geopandas as gpd
import geojson


""" THis function is used to loop through the geojson file and create a dataframe of each object in the geojson """


def create_gdf(sample_data):
    tmp = []
    polygons = []
    line = []
    for i in range(0, len(geodata['features'])):
        if i != 9:
            for j in range(0, len(geodata['features'][i]['geometry']["coordinates"])):

                if len(geodata['features'][i]['geometry']["coordinates"][j]) >= 3:
                    polygons.append(Polygon(geodata['features'][i]['geometry']["coordinates"][j]))

            tmp.append({
                'Slabel': geodata['features'][i]['properties']['Slabel'],
                'Plabel': geodata['features'][i]['properties']['Plabel'],
                'geometry': MultiPolygon(polygons)
            })
        else:
            for k in range(0, len(geodata['features'][i]['geometry']["coordinates"])):
                if len(geodata['features'][i]['geometry']["coordinates"][k]) >= 2:
                    line.append(LineString(geodata['features'][i]['geometry']["coordinates"][k]))
            tmp.append({
                'Slabel': geodata['features'][i]['properties']['Slabel'],
                'Plabel': geodata['features'][i]['properties']['Plabel'],
                'geometry': MultiLineString(line)
            })

        del polygons[:]

    gdf = gpd.GeoDataFrame(tmp)

    gdf = gdf.set_crs('epsg:32631')

    return gdf


def process_data(thin_cld, thick_cld):
    """a function to remove the overlays between the thick cloud and the thin cloud """
    difference = gpd.overlay(thin_cld, thick_cld, how='difference')

    return difference


def new_dataframe(gdf, thick_cld, difference):
    """ the function is used to create the final dataframe with the cleaned data """

    # creating a new dataframe of thick cloud and the cleaned thin cloud
    new_cloud = difference.append(thick_cld)

    # dropping rows that have overlays
    gdf_copy = gdf.drop([13, 14, 15, 16, 17])

    # adding the new cleaned cloud to the original data frame
    new_gdf = gdf_copy.append(new_cloud)

    return new_gdf


def main(data):
    """ the function is used to call the main functions and display the final result on a canvas """
    # creating the initial dataframe
    gdf = create_gdf(data)

    # Accessing the Thin and Thick clouds
    thick_cld = gdf.loc[(gdf["Slabel"] == 82)]
    thin_cld = gdf.loc[(gdf["Slabel"] == 81)]

    # getting the difference the thick cloud creates in the thin cloud
    difference = process_data(thin_cld, thick_cld)

    # creating the new cleaned dataframe
    new_gdf = new_dataframe(gdf, thick_cld, difference)

    # writing the new dataframe to geojson file into the file system
    new_gdf.to_file("clean.geojson", driver='GeoJSON')


data = "data.geojson"
geodata = geojson.load(open(data))
main(geodata)
