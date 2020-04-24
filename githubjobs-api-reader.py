import json
import os
import requests
import sqlite3
import re
from bs4 import BeautifulSoup
import matplotlib
import matplotlib.pyplot as plt

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


# =======================================================================================================================================================================================================================================================

# set up the database
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "coronavirus.db")
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
cur.execute("CREATE TABLE IF NOT EXISTS JobListings (job_id TEXT PRIMARY KEY, title TEXT, company TEXT, location TEXT, type_id INTEGER, date TEXT, description TEXT, application TEXT, remote BOOL)")

job_ids = [] # making sure there is no repeat of jobs
for city in job_data:
    for job in job_data[city]:
        if job['id'] not in job_ids:
            job_id = job['id']
            title = job['title']
            company = job['company']
            location = job['location']
            
            # date is a string of month, year
            date_list = job['created_at'].split()
            date = date_list[1] + ", " + date_list[-1]

            # type is 
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

            if 'remote' in description or 'remote' in title:
                remote = True
            else:
                remote = False

            cur.execute("INSERT INTO JobListings (job_id, title, company, location, type_id, date, description, application, remote) VALUES (?,?,?,?,?,?,?,?,?)", (job_id, title, company, location, type_id, date, description, application, remote))
            job_ids.append(job_id)
            
conn.commit()


# =======================================================================================================================================================================================================================================================

# functions for calculations

# takes a str month and an int year and returns a list of the job titles 
def get_listings_by_date(month, year, cur= cur, conn  = conn):
    month_code = month[:3] + ", " + str(year)
    cur.execute("SELECT title FROM JobListings WHERE date = ?", (month_code,))
    conn.commit()
    return cur.fetchall()

# takes a str month and an int year and returns a list of remote job titles
def remote_listings_by_date(month, year, cur= cur, conn  = conn):
    month_code = month[:3] + ", " + str(year)
    cur.execute("SELECT title FROM JobListings WHERE remote = 1 AND date = ?", (month_code,))
    return cur.fetchall()

# get the remote total listing by month 
def remote_total_by_month(month, year):
    return len(remote_listings_by_date(month, year))

# returns a list of the totals in month order
def month_totals_list(month_list, year):
    lst = []
    for month in month_list:
        lst.append(remote_total_by_month(month, year))
    return lst

# returns the yearly remote total
def yearly_total(month_list, year):
    total = 0
    lst = month_totals_list(month_list, year)
    for num in lst:
        total += num
    return total

# returns total remote listings
def get_total_remote():
    cur.execute("SELECT title FROM JobListings WHERE remote = 1")
    return len(cur.fetchall())

# returns percentage of remote listings
def get_percent_remote():
    total_remote = get_total_remote()
    cur.execute("Select * FROM JobListings")
    total_listings = len(cur.fetchall())
    return total_remote/total_listings

# returns job listings by job type
def get_listings_by_type(typ):
    cur.execute("SELECT JobListings.title FROM JobListings, JobType WHERE JobType.id = JobListings.type_id AND JobType.type = ?", (typ,))
    return cur.fetchall()

# returns number of job listings by job type
def num_listings_by_type(typ):
    return len(get_listings_by_type(typ))


#=======================================================================================================================================================================================================================================================

# code to use these functions to calculate stuff from the data base

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

remote2018_list = month_totals_list(months, 2018)
remote2019_list = month_totals_list(months, 2019)
remote2020_list = month_totals_list(months[:4], 2020)

remote2018 = yearly_total(months, 2018)
remote2019 = yearly_total(months, 2019)
remote2020 = yearly_total(months[:4], 2020)

total_remote = get_total_remote()
percent_remote = get_percent_remote()

total_analyst = num_listings_by_type("analyst")
total_python = num_listings_by_type("python")
total_developer = num_listings_by_type("developer")
total_engineer = num_listings_by_type("analyst")

# =======================================================================================================================================================================================================================================================

# creating visualizations

# remote jobs by month 2020
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.bar(months[:4], remote2020_list, color = 'lightblue')
ax.set_xlabel('month')
ax.set_ylabel('number of remote job listings')
ax.set_title('Remote job listings in 2020 by month ')
fig.savefig('remote2020.png')
plt.show()
