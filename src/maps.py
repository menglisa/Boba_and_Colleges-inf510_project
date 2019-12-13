
import folium # need to "conda install -c conda-forge folium"
from folium import plugins
from folium.plugins import HeatMap


def dot_map(df1,df2):
	ca_dot_map = folium.Map(location=[36.7783, -119.4179],
                    zoom_start = 6)

	for i in range(len(df1)):
	    folium.Marker([df1.loc[i,'latitude'], df1.loc[i,'longitude']], popup=df1.loc[i,'normalize_name'], icon=folium.Icon(color='blue',icon='university', prefix='fa')).add_to(ca_dot_map)
	    folium.Circle([df1.loc[i,'latitude'], df1.loc[i,'longitude']], radius=24140).add_to(ca_dot_map)

	stores_df = df2.dropna()

	for i,row in stores_df.iterrows():
	    folium.CircleMarker((row.latitude,row.longitude), radius=1, weight=1, color='red', fill_color='red', fill_opacity=.5).add_to(ca_dot_map)

	#save the map as an html
	ca_dot_map.save('ca_dot_map.html')
	return ca_dot_map



def heat_map(df1,df2):
	ca_heat_map = folium.Map(location=[36.7783, -119.4179],
                    zoom_start = 6)

	heat_df = df2.dropna()

	for i in range(len(heat_df)):
	    folium.CircleMarker([heat_df.loc[i,'latitude'], heat_df.loc[i,'longitude']], 
	                        radius=1, weight=1, color='red', fill_color='red', fill_opacity=.5).add_to(ca_heat_map)
	    
	ca_heat_map.add_child(plugins.HeatMap(data=heat_df[['latitude', 'longitude']].values, radius=25, blur=10))

	for i in range(len(df1)):
	    folium.Marker([df1.loc[i,'latitude'], df1.loc[i,'longitude']], 
	                  popup=df1.loc[i,'normalize_name'],
	                  icon=folium.Icon(color='blue',icon='university', prefix='fa')).add_to(ca_heat_map)

	#save the map as an html
	ca_heat_map.save('ca_heat_map.html')
	return ca_heat_map





if __name__ == "__main__":
    print('You called me from the command line! Please import as module in meng_lisa.py')
else:
    print(__name__ , 'was imported as a module!')