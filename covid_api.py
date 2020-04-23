#COVID Api
import json
import unittest
import os
import requests
import operator
import sqlite3
import matplotlib
import matplotlib.pyplot as plt

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
    cur.execute("INSERT INTO Countries (country, country_code, total_confirmed, total_deaths, total_recovered) VALUES (?, ?, ?, ?, ?)",(country, country_code, total_confirmed, total_deaths_, total_recovered))
conn.commit()



cur.execute("DROP TABLE IF EXISTS Global")
cur.execute("CREATE TABLE Global (total_confirmed_global INTEGER PRIMARY KEY, total_deaths_global INTEGER, total_recovered_global INTEGER)")

globe = covid_data['Global']
total_confirmed_global = globe.get('TotalConfirmed')
total_deaths_global = globe.get('TotalDeaths')
total_recovered_global = globe.get('TotalRecovered')

cur.execute("INSERT INTO Global (total_confirmed_global, total_deaths_global, total_recovered_global) VALUES (?, ?, ?)",(total_confirmed_global, total_deaths_global, total_recovered_global))


conn.commit()

# =======================================================================================================================================================================================================================================================

# functions for calculations:

#retrieve the number of confirmed cases
def numberOfConfirmed(c, cur = cur, conn = conn):
    cur.execute('SELECT Total_confirmed FROM Countries WHERE Country = ?', (c,))
    conn.commit()
    return cur.fetchone()[0]


#retrieve the number of deaths
def numberOfDeaths(c, cur = cur, conn = conn):
    cur.execute('SELECT Total_deaths FROM Countries WHERE Country = ?', (c,))
    conn.commit()
    return cur.fetchone()[0]


#retrieve the number of recovered
def numberOfRecovered(c, cur = cur, conn = conn):
    cur.execute('SELECT Total_recovered FROM Countries WHERE Country = ?', (c,))
    conn.commit()
    return cur.fetchone()[0]



#calculate the percentage of confirmed of the global cases
def percentageOfConfirmed(c, cur = cur, conn = conn):
    number_of_confirmed = numberOfConfirmed(c)
    cur.execute('SELECT Total_confirmed_global FROM Global')
    conn.commit()
    number_global = cur.fetchone()[0]
    percentage = (number_of_confirmed / number_global)
    return percentage


#calculate the percentage of global deaths
def percentageOfDeaths(c, cur = cur, conn = conn):
    number_of_deaths = numberOfDeaths(c)
    cur.execute('SELECT Total_deaths_global FROM Global')
    conn.commit()
    number_global = cur.fetchone()[0]
    percentage = (number_of_deaths / number_global)
    return percentage



#calculate the percentage of global recovered
def percentageOfRecovered(c, cur = cur, conn = conn):
    number_of_recovered = numberOfRecovered(c)
    cur.execute('SELECT Total_recovered_global FROM Global')
    conn.commit()
    number_global = cur.fetchone()[0]
    percentage = (number_of_recovered / number_global)
    return percentage



#=======================================================================================================================================================================================================================================================

# code to use these functions to calculate stuff from the data base


#total confirmed cases in the united states
print(numberOfConfirmed('United States of America'))

#total deaths in the united states
print(numberOfDeaths('United States of America'))

#total recovered covid cases in the united states
print(numberOfRecovered('United States of America'))



#percentage of united staes confirmed cases of the total global confirmed cases
print(percentageOfConfirmed('United States of America'))


#percentage of united staes deaths  of the total global deaths
print(percentageOfDeaths('United States of America'))


#percentage of united staes recovered cases of the total global recovered cases
print(percentageOfRecovered('United States of America'))


# visualizations 

cur.execute("SELECT coronavirus_hits FROM NYTPostData")
hits = cur.fetchall()
total = 0
for hit in hits:
    total += hit[0]
numConfirmed = numberOfConfirmed('United States of America')

x = ["NYT mentions", "Confirmed Cases"]
y = [total, numConfirmed]

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.bar(x, y, color = 'red')
ax.set_title('Number of US cases vs. mentions in NYT')
fig.savefig('casesVSmentions.png')
plt.show()

cur.execute("SELECT total_deaths_global FROM Global")
global_deaths = cur.fetchone()[0]
labels = ["United States", "Global"]
sizes = [numberOfDeaths('United States of America'), global_deaths]  
explode = (0.1, 0)

fig2 = plt.figure(figsize=(10,5))
ax2 = fig2.add_subplot(111)
ax2.pie(sizes, explode = explode, labels = labels, autopct = '%1.1f%%', shadow = True, startangle = 90)
ax2.axis('equal')
ax2.set_title('Percentage of US COVID-19 deaths')
fig2.savefig('percentage_deaths.png')
plt.show()