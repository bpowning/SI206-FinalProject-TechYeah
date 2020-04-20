#COVID Api
import json
import unittest
import os
import requests
import operator
import sqlite3


#set up database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn



base_url = 'https://api.covid19api.com/summary'
result = requests.get(base_url)
covid_data = json.loads(result.text)

#get confirmed cases and confirmed deaths
def setUpCountryTable(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS Countries")
    cur.execute("CREATE TABLE Countries (total_confirmed INTEGER PRIMARY KEY, country TEXT, country_code TEXT, total_deaths INTEGER, total_recovered INTEGER)")
    countries = covid_data['Countries']
    for x in countries:
        country = x.get('Country')
        country_code = x.get('CountryCode')
        total_confirmed = x.get('TotalConfirmed')
        total_deaths_ = x.get('TotalDeaths')
        total_recovered = x.get('TotalRecovered')

        cur.execute("INSERT INTO Countries (country, country_code, total_confirmed, total_deaths, total_recovered) VALUES (?, ?, ?, ?, ?)",(country, country_code, total_confirmed, total_deaths_, total_recovered))
    conn.commit()

def setUpGlobalTable(data, cur, conn):
    cur.execute("DROP TABLE IF EXISTS Global")
    cur.execute("CREATE TABLE Countries (total_confirmed INTEGER PRIMARY KEY, total_deaths INTEGER, total_recovered INTEGER)")
    globe = covid_data['Global']
    for x in globe:
        total_confirmed = x.get('TotalConfirmed')
        total_deaths = x.get('TotalDeaths')
        total_recovered = x.get('TotalRecovered')

        cur.execute("INSERT INTO Global (total_confirmed, total_deaths, total_recovered) VALUES (?, ?, ?)",(total_confirmed, total_deaths, total_recovered))
    conn.commit()

db = 'Coronavirus'
set_up = setUpDatabase(db)
table1 = setUpCountryTable(covid_data)
table2 = setUpGlobalTable(covid_data)


