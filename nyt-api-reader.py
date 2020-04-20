import sqlite3
import json
import os
import requests
import re

# get directory path and create cache file
path = os.path.dirname(os.path.realpath(__file__))
nyt_file = path + '/' + "nyt_covid_data.json"

# if there is data in the cache file, load the content into a dictionary or leave it empty
def read_cache(cache_file):
    try:
        file = open(cache_file, 'r')
        cache_dict = json.loads(file.read())
        file.close()
        return cache_dict
    except:
        cache_dict = {}
        return cache_dict

# writes the JSON to the cache file and saves the results
def write_cache(cache_file, cache_dict):
    file_path = os.path.join(os.path.dirname(__file__), cache_file)
    file = open(file_path, 'w')
    file.write(json.dumps(cache_dict))

"""
BASE CALL FOR NYT ARCHIVE API
https://api.nytimes.com/svc/archive/v1/2019/1.json?api-key=yourkey

BASE CALL FOR NYT ARTICLE SEARCH API
"https://api.nytimes.com/svc/search/v2/articlesearch.json?q=election&api-key=yourkey"
"""

# NYT API key and URL for Archive from 2019 and 2020
# and Article Search for term "________"
API_KEY = "GVoB95VLbFRPEUbpesKu3DqCTVritOM3"

def url_for_month_2k19(month):
    base_url = "https://api.nytimes.com/svc/archive/v1/2019/" + month + ".json?api-key=" + API_KEY
    return base_url

def url_for_month_2k20(month):
    base_url = "https://api.nytimes.com/svc/archive/v1/2020/" + month + ".json?api-key=" + API_KEY
    return base_url

def url_for_article_search():
    base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?q=election&api-key=" + API_KEY
    return base_url

# get data from NYT API Call
def get_data(base_url, cache_file = nyt_file):
    cache_dict = read_cache(cache_file)
    if base_url in cache_dict:
        return cache_dict[base_url]
    else:
        request = requests.get(base_url) 
        cache_dict[base_url] = json.loads(request.text)
        write_cache(cache_file, cache_dict)
        return cache_dict[base_url]

# add data to nyt_covid_data.json
months_in_19 = ["10", "11", "12"]
for month in months_in_19:
    base_url = url_for_month_2k19(month)
    get_data(base_url)

months_in_20 = ["1", "2", "3", "4"]
for month in months_in_20:
    base_url = url_for_month_2k20(month)
    get_data(base_url)

# read cached file
nyt_data = read_cache("nyt_covid_data.json")

# set up database
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/'+ "NYT.db")
cur = conn.cursor()

# set up "articlesxmonth" for all articles by month
# set up "covidarticlesxmonth" for all covid articles by month
# set up "percentcovidarticles" for percentage of articles about corona
months = ["oct", "nov", "dec", "jan", "feb", "mar", "apr"]
articlesxmonth = []
covidarticlesxmonth=[]
percentcovidarticles = []
percent_covidxmonth = 0.000000
url_break = 0
for url in nyt_data:
    if url_break < 7:
        x = nyt_data[url]['response']['meta']['hits']
        articlesxmonth.append(x)
        num_coronavirus_articles = 0
        for doc in nyt_data[url]['response']['docs']:
            for keyword in doc['keywords']:
                if keyword['value'] == 'Coronavirus (2019-nCoV)':
                    num_coronavirus_articles += 1
        covidarticlesxmonth.append(num_coronavirus_articles)
        url_break += 1
for i in range(len(articlesxmonth)):
    percent_covidxmonth = (covidarticlesxmonth[i]/articlesxmonth[i])
    percentcovidarticles.append(percent_covidxmonth)

cur.execute("DROP TABLE IF EXISTS ArticlesxMonth")
cur.execute("CREATE TABLE IF NOT EXISTS ArticlesxMonth (month_id INTEGER PRIMARY KEY, month STRING, total_hits INTEGER, coronavirus_hits INTEGER, percent_of_covid_articles FLOAT)")

for i in range(len(articlesxmonth)):
    cur.execute("INSERT INTO ArticlesxMonth (month_id, month, total_hits, coronavirus_hits, percent_of_covid_articles) VALUES (?,?,?,?,?)", (i, months[i], articlesxmonth[i], covidarticlesxmonth[i], percentcovidarticles[i]))
conn.commit()