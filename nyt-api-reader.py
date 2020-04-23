import sqlite3
import json
import os
import requests
import re
import matplotlib
import matplotlib.pyplot as plt

# NYT API Reader accessed to get all articles and articles created per month about
# the COVID-19 epidemic

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
"""

# NYT API key and URL for Archive from 2019 and 2020

API_KEY = "GVoB95VLbFRPEUbpesKu3DqCTVritOM3"

def url_for_month_2k19(month):
    base_url = "https://api.nytimes.com/svc/archive/v1/2019/" + month + ".json?api-key=" + API_KEY
    return base_url

def url_for_month_2k20(month):
    base_url = "https://api.nytimes.com/svc/archive/v1/2020/" + month + ".json?api-key=" + API_KEY
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
# used these specific months to track increase of posts about coronavirus last six months
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
conn = sqlite3.connect(path + '/'+ "coronavirus.db")
cur = conn.cursor()

# declaring lists and variables for NYTPostData table
# months list matches order in which data was collected for each month (see months_in_19 and months_in_20)
months = ["oct", "nov", "dec", "jan", "feb", "mar", "apr"]
postsxmonth = []
covidpostsxmonth = []
percentcovidposts = []
percent_covidxmonth = 0.000000
# declaring lists for NYTCoronavirusPosts table
post_urls = []
post_headlines = []
post_pub_dates = []
all_post_simple_pub_dates = []
cv_post_simple_pub_dates = []
post_snippets = []
cv_type_of_post = []
# url_break used to stop url loop before it hits error handling urls (Error 400)
url_break = 0

# collect total number of posts per month and all simple_pub_dates for all posts
# collect url, headline, pub_date, simple_pub_date, snippet and post_type for each post with
# the keyword 'Coronavirus (2019-nCoV)'
for url in nyt_data:
    if url_break < 7:
        x = nyt_data[url]['response']['meta']['hits']
        postsxmonth.append(x)
        for doc in nyt_data[url]['response']['docs']:
            all_post_simple_pub_dates.append((doc['pub_date'])[0:7])
            for keyword in doc['keywords']:
                # checking for mentions of Coronavirus in keywords, headlines and urls specifically
                # (and not snippets) as certain snippets might mention coronavirus but not about it.
                if (keyword['value'] == 'Coronavirus (2019-nCoV)') or (('Coronavirus' or 'coronavirus' or 'COVID-19') in doc['headline']['main']) or ('coronavirus' in doc['web_url']):
                    if (doc['web_url'] not in post_urls) and (doc['headline']['main'] not in post_headlines) and (doc['snippet'] not in post_snippets) and (doc['pub_date'] not in post_pub_dates):
                        post_urls.append(doc['web_url'])
                        post_pub_dates.append(doc['pub_date'])
                        cv_post_simple_pub_dates.append((doc['pub_date'])[0:7])
                        post_snippets.append(doc['snippet'])
                        headline_transition = doc['headline']['main']
                        post_headlines.append(headline_transition)
                        cv_type_of_post.append(doc['document_type'])
        url_break += 1

# create NYTCoronavirusPosts table to hold info about all posts with keyword coronavirus
cur.execute("DROP TABLE IF EXISTS NYTCoronavirusPosts")
cur.execute("CREATE TABLE IF NOT EXISTS NYTCoronavirusPosts (post_id INTEGER PRIMARY KEY, url STRING, headline STRING, pub_date STRING, pub_date_simple STRING, snippet STRING, post_type STRING)")

# insert data into NYTCoronavirusPosts table
for i in range(len(post_urls)):
    cur.execute("INSERT INTO NYTCoronavirusPosts (post_id, url, headline, pub_date, pub_date_simple, snippet, post_type) VALUES (?,?,?,?,?,?,?)", (i, post_urls[i], post_headlines[i], post_pub_dates[i], cv_post_simple_pub_dates[i], post_snippets[i], cv_type_of_post[i]))
conn.commit()

# get simple dates from all posts in collected NYT Data
# should get following list:
# simple_date_list = ['2019-10', '2019-11', '2019-12', '2020-01', '2020-02', '2020-03', '2020-04']
simple_date_list = []
for simple_date in all_post_simple_pub_dates:
    if simple_date not in simple_date_list:
        simple_date_list.append(simple_date)

# Calculations to get number of posts by month with matching simple date
def getNYTCoronaPostsNumberbyMonth(chosen_pub_date, cur, conn):
    cur.execute("SELECT url, headline, pub_date, pub_date_simple, snippet, post_type from NYTCoronavirusPosts WHERE (pub_date_simple == ?)", (chosen_pub_date,))
    corona_posts_bymonth = cur.fetchall()
    conn.commit()
    return corona_posts_bymonth

# add number of posts with keyword 'Coronavirus (2019-nCoV)' to covidpostsxmonth by specific month
for date in simple_date_list:
    list_of_posts = getNYTCoronaPostsNumberbyMonth(date, cur, conn)
    covidpostsxmonth.append(len(list_of_posts))

# create percentages list based off of covidpostsxmonth[i]
for i in range(len(postsxmonth)):
    percent_covidxmonth = (covidpostsxmonth[i]/postsxmonth[i])
    percentcovidposts.append(percent_covidxmonth)

# create NYTPostData table to hold all data about coronavirus posts
cur.execute("DROP TABLE IF EXISTS NYTPostData")
cur.execute("CREATE TABLE IF NOT EXISTS NYTPostData (month_id INTEGER PRIMARY KEY, month STRING, total_hits INTEGER, coronavirus_hits INTEGER, percent_of_covid_posts FLOAT)")

# insert data into NYTPostData table
for i in range(len(postsxmonth)):
    cur.execute("INSERT INTO NYTPostData (month_id, month, total_hits, coronavirus_hits, percent_of_covid_posts) VALUES (?,?,?,?,?)", (i, months[i], postsxmonth[i], covidpostsxmonth[i], percentcovidposts[i]))
conn.commit()

cur.execute("SELECT month, percent_of_covid_posts FROM NYTPostData")
percents = cur.fetchall()

months = []
percent_lists = []
for percent in percents:
    months.append(percent[0])
    percent_lists.append(percent[1])

# visualizations
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.plot(months, percent_lists, color = 'red')
ax.set_xlabel('month')
ax.set_ylabel('percentage of COVID-19 mentions')
ax.set_title('Percentage of New York Times COVID-19 mentions by month')
fig.savefig('percent_mentions.png')
plt.show()
