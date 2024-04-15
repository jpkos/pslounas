#%%
import numpy as np
import pandas as pd
import requests
import os
from datetime import datetime
from flask import Flask, render_template
import folium
from folium.plugins import FloatImage
from folium import Element
import yaml
from bs4 import BeautifulSoup

import data_handlers as dh
#%%
html = '''
<div id="maptitle" style="position: fixed; top: 20px; left: 100px; z-index: 9999; font-size: 48px; color: black; background-color: white; padding: 5px;">
    <h4>Pasilan Seudun Lounaat</h4>
</div>
<script>
    var title = L.control({position: 'topleft'});
    title.onAdd = function (map) {
        var div = L.DomUtil.get("maptitle");
        return div;
    };
    title.addTo({{this}});
</script>
'''
title_html = Element(html)
app = Flask(__name__)

@app.route('/')
def index():
    restaurant_data = dh.load_restaurants()
    start_coords = (60.19912857374085, 24.940578211739854)  
    folium_map = folium.Map(location=start_coords,
                            zoom_start=16,
                            tiles='CartoDB positron')
    folium.Marker(
                location=start_coords,
                tooltip='HSL'
            ).add_to(folium_map)
    for restaurant in restaurant_data:
        if restaurant['source'] == 'website':
            restaurant_menu, _, _ = dh.fetch_menu_url(restaurant['url'])
        elif restaurant['source'] == 'rss':
            restaurant_menu = dh.fetch_menu_rss(restaurant['url'])
        popup_content = f'<b>{restaurant["name"]} (<a href="{restaurant["url"]}" target="_blank">{restaurant["url"]}</a>)</b><br><br>'
        for day, menu in restaurant_menu.items():
            popup_content += '<b>{}</b><br>{}<br><br>'.format(day, menu.replace('\n', '<br>'))
        folium.Marker(
                location=(restaurant['latitude'], restaurant['longitude']),
                popup=folium.Popup(popup_content, max_width=450),
                tooltip=restaurant['name'],
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(folium_map)
    folium_map.get_root().html.add_child(title_html)
    return folium_map._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)
# %%
