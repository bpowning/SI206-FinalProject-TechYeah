import sqlite3
import json
import os
import requests
import urllib.request, urllib.parse, urllib.error

# https://jobs.github.com/api

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

# functions to create a url based on the different parameters you want to search
def url_by_location(location):
    base_url = "https://jobs.github.com/positions.json?" + "location=" + location
    return base_url

def url_by_jobtype(description):
    base_url = "https://jobs.github.com/positions.json?" + "description=" + description
    return base_url

def url_by_both(location, description):
    base_url = "https://jobs.github.com/positions.json?" + "location=" + location + "&description=" + description
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

url = url_by_location("newyork")
get_data(url)