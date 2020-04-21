#COVID Api
import json
import unittest
import os
import requests
import operator
import sqlite3

path = os.path.dirname(os.path.realpath(__file__))
covid_file = path + '/' + "covid_data.json"

def read_cache(cache_file):
    try:
        file = open(cache_file, 'r')
        cache_dict = json.loads(file.read())
        file.close()
        return cache_dict
    except:
        cache_dict = {}
        return cache_dict


def write_cache(cache_file, cache_dict):
    file_path = os.path.join(os.path.dirname(__file__), cache_file)
    file = open(file_path, 'w')
    file.write(json.dumps(cache_dict))

base_url = 'https://api.covid19api.com/summary'


def get_data(base_url, cache_file = covid_file):
    cache_dict = read_cache(cache_file)
    if base_url in cache_dict:
        return cache_dict[base_url]
    else:
        request = requests.get(base_url)
        cache_dict[base_url] = json.loads(request.text)
        write_cache(cache_file, cache_dict)
        return cache_dict[base_url]

get_data(base_url)

covid_data = read_cache('covid_data.json')
covid_data = covid_data["https://api.covid19api.com/summary"]

#set up database
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + 'coronavirus.db')
cur = conn.cursor()

country_lst = []
for c in covid_data:
    for a in covid_data["Countries"]:
        if a['Country'] not in country_lst:
            country_lst.append(a['Country'])


cur.execute("DROP TABLE IF EXISTS Countries")
cur.execute("CREATE TABLE Countries (country TEXT PRIMARY KEY, country_code TEXT, total_confirmed INTEGER,  total_deaths INTEGER, total_recovered INTEGER)")
countries = covid_data['Countries']
for x in countries:
    country = x.get('Country')
    country_code = x.get('CountryCode')
    total_confirmed = x.get('TotalConfirmed')
    total_deaths_ = x.get('TotalDeaths')
    total_recovered = x.get('TotalRecovered')




#for i in range(len(country_lst)):
    cur.execute("INSERT INTO Countries (total_confirmed, country, country_code, total_deaths, total_recovered) VALUES (?, ?, ?, ?, ?)",(total_confirmed, country, country_code, total_deaths_, total_recovered))
conn.commit()



cur.execute("DROP TABLE IF EXISTS Global")
cur.execute("CREATE TABLE Global (total_confirmed_global INTEGER PRIMARY KEY, total_deaths_global INTEGER, total_recovered_global INTEGER)")

globe = covid_data['Global']
total_confirmed_global = globe.get('TotalConfirmed')
total_deaths_global = globe.get('TotalDeaths')
total_recovered_global = globe.get('TotalRecovered')

cur.execute("INSERT INTO Global (total_confirmed_global, total_deaths_global, total_recovered_global) VALUES (?, ?, ?)",(total_confirmed_global, total_deaths_global, total_recovered_global))


conn.commit()




