#%%
import numpy as np
import requests
import os
from datetime import datetime
from flask import Flask, render_template
import folium
import yaml
from bs4 import BeautifulSoup
import feedparser
#%%

def load_restaurants():
    with open("restaurants.yaml", 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return []
        
def fetch_menu_rss(url):
    feed = feedparser.parse(url)
    menu_items = {}
    for e in feed['entries']:
        weekday = e['title'].split(' ')[0]
        item_text = e['summary']
        menu_items[weekday] = item_text
    return menu_items

def fetch_menu_url(url):
    weekdays_finnish = ['maanantai', 'tiistai', 'keskiviikko', 'torstai', 'perjantai', 'lauantai', 'sunnuntai']

    try:

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        menu_sections = soup.find_all(['h3', 'p', 'li', 'a', 'div'])
        weekday_idx = []
        menu_items = {}
        for i, tag in enumerate(menu_sections):
            if any(weekday in tag.get_text().lower() for weekday in weekdays_finnish):
                weekday_idx.append(i)
                
        for j, idx in enumerate(weekday_idx):
            weekday = menu_sections[idx].get_text().split(' ')[0]
            if weekday.lower() not in weekdays_finnish:
                continue
            items = []
            if len(menu_sections[idx].get_text())>=20:
                sub_items = list(menu_sections[idx].children)
                for si in sub_items[1:]:
                    items.append(si.get_text())
            k = idx+1
            if idx == max(weekday_idx):
                idx_max = idx+5
            else:
                idx_max = weekday_idx[j+1]
            while k < idx_max:
                item_text = menu_sections[k].get_text().strip()
                if item_text not in ['', ' ', 'Lounasbuffet', '\t', '\n']:
                    items.append(item_text)
                k = k + 1
            menu_items[weekday] = '\n'.join(items)

        return menu_items, menu_sections, weekday_idx

    except requests.RequestException as e:
        print(f"Error fetching the menu: {e}")
        return []

#%%