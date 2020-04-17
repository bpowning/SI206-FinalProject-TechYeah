import sqlite3
import json
import os
import requests

# https://jobs.github.com/api

# get directory path and create cache file
dir_path = os.path.dirname(os.path.realpath(__file__))
CACHE_FNAME = dir_path + '/' + "cache_jobs.json"

# if there is data in the cache file, load the content into a dictionary or leave it empty
try:
    cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") # Try to read the data from the file
    cache_contents = cache_file.read()  # If it's there, get it into a string
    CACHE_DICTION = json.loads(cache_contents) # And then load it into a dictionary
    cache_file.close() # Close the file, we're good, we got the data in a dictionary.
except:
    CACHE_DICTION = {}

# writes the JSON to the cache file and saves the results
path_to_file = os.path.join(os.path.dirname(__file__), CACHE_FNAME)
with open(path_to_file, 'w') as f:
    x = json.dumps(CACHE_DICTION)
    f.write(json.dumps(CACHE_DICTION))

<<<<<<< HEAD
# function to create a url based on the different parameters you want to search
def create_base_url(description = "", location = "", lat = "", long = "", full_time = ""):
    base_url = "https://jobs.github.com/positions?" + 

=======
# functions to create a url based on the different parameters you want to search
def url_by_location(location):
    base_url = "https://jobs.github.com/positions?" + "location=" + location
    return base_url

def url_by_jobtype(description):
    base_url = "https://jobs.github.com/positions?" + "description=" + description
    return base_url

def url_by_both(location, description):
    base_url = "https://jobs.github.com/positions?" + "location=" + location + "&description=" + description
    return base_url

# function to get data from an API call
>>>>>>> 8797668f814c803182516e441d830283cece0eeb
