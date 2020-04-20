import json
import os
import requests
import sqlite3
import re
from bs4 import BeautifulSoup

# get directory path and create cache file
path = os.path.dirname(os.path.realpath(__file__))
jobs_file = path + '/' + "cache_jobs.json"

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

# functions to create a url based on location
def url_by_location(location):
    base_url = "https://jobs.github.com/positions.json?" + "location=" + location
    return base_url

def url_by_description(description):
    base_url = "https://jobs.github.com/positions.json?" + "description=" + description
    return base_url

# get data from an API call
def get_data(base_url, cache_file = jobs_file):
    cache_dict = read_cache(cache_file)
    if base_url in cache_dict:
        return cache_dict[base_url]
    else:
        request = requests.get(base_url) 
        cache_dict[base_url] = json.loads(request.text)
        write_cache(cache_file, cache_dict)
        return cache_dict[base_url]

# add data to cache_jobs.json
cities = ["newyork", "boston", "chicago", "sanfrancisco", "losangeles", "seattle", "phillidelphia", "newjersey", "detroit", "texas"]
for city in cities:
    base_url = url_by_location(city)
    get_data(base_url)

types = ["engineer", "developer", "remote"]
for typ in types:
    base_url = url_by_description(typ)
    get_data(base_url)

# read the cache file
job_data = read_cache('cache_jobs.json')

# set up the database
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "githubjobs.db")
cur = conn.cursor()

# set up a table called Job Type for all types of job listings
cur.execute("DROP TABLE IF EXISTS JobType")
cur.execute("CREATE TABLE IF NOT EXISTS JobType (id INTEGER PRIMARY KEY, type TEXT)")

job_types = ["analyst", "python", "developer", "engineer"]
for i in range(len(job_types)):
    cur.execute("INSERT INTO JobType (id,type) VALUES (?,?)",(i,job_types[i]))
conn.commit()

# set up a table called JobListings for all 2020 job listings
cur.execute("DROP TABLE IF EXISTS JobListings")
cur.execute("CREATE TABLE IF NOT EXISTS JobListings (job_id TEXT PRIMARY KEY, company TEXT, location TEXT, type_id INTEGER, date INTEGER, description TEXT, application TEXT)")

job_ids = [] # making sure there is no repeat of jobs
for city in job_data:
    for job in job_data[city]:
        if job['id'] not in job_ids:
            job_id = job['id']
            company = job['company']
            location = job['location']
            date = int(job['created_at'].split(' ')[-1])

            type_name = job['title'].lower()
            if "analyst" in type_name:
                typ = "analyst"
            elif "python" in type_name:
                typ = "python"
            elif "engineer" in type_name:
                typ = "engineer"
            elif "developer" in type_name:
                typ = "developer"
            
            cur.execute("SELECT id FROM JobType WHERE type = ?", (typ,))
            type_id = cur.fetchone()[0]

            soup = BeautifulSoup(job['description'], 'html.parser')
            description = soup.get_text()

            soup = BeautifulSoup(job['how_to_apply'], 'html.parser')
            application = soup.get_text()

            cur.execute("INSERT INTO JobListings (job_id, company, location, type_id, date, description, application) VALUES (?,?,?,?,?,?,?)", (job_id, company, location, type_id, date, description, application))
            job_ids.append(job_id)
            
conn.commit()