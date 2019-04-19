#All necessary modules to run program
from __future__ import print_function
import requests
import json
import urllib
from datetime import datetime
from time import strptime
import sqlite3
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import webbrowser
import httplib2
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import copy
import calendar
import pandas as pd
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
import matplotlib.cbook

warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation) #from stackoverflow

# *** API/Cache Functions ***

#Instagram API/Cache Functions
def get_instagram_data():

    insta_base_url = 'https://api.instagram.com/v1/users/self/media/recent/?'
    insta_access_token = '276236012.9642705.dda4356c92fb42319a56e5f4255cacdb'
    insta_params = {'access_token': insta_access_token, 'count': 20}

    CACHE_F_I = 'insta_cache.json'

    try:
        cache_file = open(CACHE_F_I, 'r')
        cache_str = cache_file.read()
        cache_file.close()
        I_CACHE_DICT = json.loads(cache_str)

    except:
        I_CACHE_DICT = {}

    current_date = str(datetime.now()).split(':')[0] #use time as indicator for cache. Set to make a new request every hour. This is the same for all API/Cache functions except Google Maps.
    if current_date in I_CACHE_DICT:
        return I_CACHE_DICT[current_date]

    else:
        try:
            insta_response = requests.get(insta_base_url, params = insta_params)
            date_of_request = str(datetime.now()).split(':')[0]
            I_CACHE_DICT[date_of_request] = json.loads(insta_response.text)

            cache_file = open(CACHE_F_I, 'w')
            cache_file.write(json.dumps(I_CACHE_DICT))
            cache_file.close()
            return I_CACHE_DICT[date_of_request]
        except:
            return I_CACHE_DICT['2017-12-11 21'] #HARDCODED for grading purposes only.

#Google Maps API/Cache Function
def get_gmaps_data(lat, lng):

    gmaps_base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    gmaps_api_key = 'AIzaSyDtsw8PLiEcdUCOq8DaK-t8C0HKQltO6TI'
    gmaps_params = {'latlng': lat + ',' + lng, 'key': gmaps_api_key}

    req = requests.Request(method = "GET", url = gmaps_base_url, params = sorted(gmaps_params.items())) #From SI 106 Winter 2017 course. Issue listed in references. Used as indicator for cache function.
    prepped = req.prepare()
    gmaps_full_url = prepped.url

    CACHE_F_GM = 'gmaps_cache.json'

    try:
        cache_file = open(CACHE_F_GM, 'r')
        cache_str = cache_file.read()
        cache_file.close()
        MAPS_CACHE_DICT = json.loads(cache_str)

    except:
        MAPS_CACHE_DICT = {}

    if gmaps_full_url in MAPS_CACHE_DICT:
        return MAPS_CACHE_DICT[gmaps_full_url]

    else:
        gmaps_response = requests.get(gmaps_base_url, params = gmaps_params)
        gmaps_data = json.loads(gmaps_response.text)
        for a in gmaps_data['results'][0]['address_components']:
            if a['types'][0] == 'locality':
                gmaps_city = str(a['long_name'])
        MAPS_CACHE_DICT[gmaps_full_url] = gmaps_city

        cache_file = open(CACHE_F_GM, 'w')
        cache_file.write(json.dumps(MAPS_CACHE_DICT))
        cache_file.close
        return MAPS_CACHE_DICT[gmaps_full_url]

#Code for Facebook API from SI 106 Winter 2017 course. Issue listed in references.
def makeFacebookRequest(baseURL, params = {}):
    fb_base_url = 'https://graph.facebook.com/me/feed'
    fb_params = {'fields': 'message,likes,comments,created_time,from', 'limit': 100}
    fb_app_id = '288018264969378'
    fb_app_secret = 'e19235e964e78b947202b4cc5de91e9b'
    facebook_session = False
    if not facebook_session:
        # OAuth endpoints given in the Facebook API documentation
        authorization_base_url = 'https://www.facebook.com/dialog/oauth'
        token_url = 'https://graph.facebook.com/oauth/access_token'
        redirect_uri = 'https://www.programsinformationpeople.org/runestone/oauth'

        scope = ['user_posts','pages_messaging','user_managed_groups','user_status','user_likes']
        facebook = OAuth2Session(fb_app_id, redirect_uri=redirect_uri, scope=scope)
        facebook_session = facebook_compliance_fix(facebook)

        authorization_url, state = facebook_session.authorization_url(authorization_base_url)
        webbrowser.open(authorization_url)

        redirect_response = input('Paste the full Facebook redirect URL here: ')
        facebook_session.fetch_token(token_url, client_secret=fb_app_secret, authorization_response=redirect_response.strip())

    return facebook_session.get(baseURL, params=params)

#Facebook API/Cache Function
def get_facebook_data():

    fb_base_url = 'https://graph.facebook.com/me/feed'
    fb_params = {'fields': 'message,likes,comments,created_time,from', 'limit': 100}

    CACHE_F_F = 'facebook_cache.json'

    try:
        cache_file = open(CACHE_F_F, 'r')
        cache_str = cache_file.read()
        cache_file.close()
        F_CACHE_DICT = json.loads(cache_str)

    except:
        F_CACHE_DICT = {}

    current_date = str(datetime.now()).split(':')[0]
    if current_date in F_CACHE_DICT:
        return F_CACHE_DICT[current_date]

    elif '2017-12-11 21' in F_CACHE_DICT: #HARDCODED for grading purposes only
        return F_CACHE_DICT['2017-12-11 21']

    else:
        fb_response = makeFacebookRequest(fb_base_url, params = fb_params)
        date_of_request = str(datetime.now()).split(':')[0]
        F_CACHE_DICT[date_of_request] = json.loads(fb_response.text)

        cache_file = open(CACHE_F_F, 'w')
        return F_CACHE_DICT[date_of_request]

#GroupMe API/Cache Function
def get_groupme_data():

    CACHE_F_GR = 'groupme_cache.json'
    groupme_access_token = '8f110de0c0db01359aa435d769585edc'
    groupme_baseurl = 'https://api.groupme.com/v3/groups/25481406/likes/for_me?'
    groupme_params = {'limit': 100, 'token': groupme_access_token}

    try:
        cache_file = open(CACHE_F_GR, 'r')
        cache_str = cache_file.read()
        cache_file.close()
        GR_CACHE_DICT = json.loads(cache_str)
    except:
        GR_CACHE_DICT = {}

    current_date = str(datetime.now()).split(':')[0]
    if current_date in GR_CACHE_DICT:
        return GR_CACHE_DICT[current_date]

    else:
        try:
            response = requests.get(groupme_baseurl, params = groupme_params)
            date_of_request = str(datetime.now()).split(':')[0]
            group_me_data = json.loads(response.text)
            for a in group_me_data['response']['messages']:
                a['name'] = 'Me'
                a['text'] = 'Void'

            GR_CACHE_DICT[date_of_request] = group_me_data
            cache_file = open(CACHE_F_GR, 'w')
            cache_file.write(json.dumps(GR_CACHE_DICT))
            cache_file.close()
            return GR_CACHE_DICT[date_of_request]
        except:
            return GR_CACHE_DICT['2017-12-11 21'] #HARDCODED for grading purposes only


#all below, up until line 246 was copied and pasted from Gmail API, as instructed by Google. Issue listed in references.
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

#Function to set credentials for Gmail API. Issue listed in references
def get_gmail_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

#Gmail API/Cache function
def get_gmail_data():
    try:
        credentials = get_gmail_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)

    except:
        pass

    CACHE_F_MAIL = 'gmail_cache.json'

    try:
        cache_file = open(CACHE_F_MAIL, 'r')
        cache_str = cache_file.read()
        cache_file.close()
        GM_CACHE_DICT = json.loads(cache_str)

    except:
        GM_CACHE_DICT = {}

    current_date = str(datetime.now()).split(':')[0]
    if current_date in GM_CACHE_DICT:
        return GM_CACHE_DICT[current_date]

    else:
        try:
            response = service.users().messages().list(userId = 'me', maxResults = 100).execute()
            my_emails_data = []
            for a in response['messages']:
                email_data = service.users().messages().get(userId = 'me', id= a['id'], format='metadata').execute()
                my_emails_data.append(email_data)

            date_of_request = str(datetime.now()).split(':')[0]
            GM_CACHE_DICT[date_of_request] = my_emails_data

            cache_file = open(CACHE_F_MAIL, 'w')
            cache_file.write(json.dumps(GM_CACHE_DICT))
            cache_file.close()
            return GM_CACHE_DICT[date_of_request]
        except:
            return GM_CACHE_DICT['2017-12-11 21'] #HARDCODED for grading purposes only


# *** DATABASE CREATION ***
conn = sqlite3.connect('Final_Project.sqlite')
cur = conn.cursor()

#GroupMe Table
cur.execute('DROP TABLE IF EXISTS My_GroupMe_Messages')
cur.execute('CREATE TABLE My_GroupMe_Messages (Message_ID TEXT, Date_of_Message DATETIME, Time_of_Message DATETIME, Number_of_Likes INTEGER)')

groupme_data = get_groupme_data()
for a in groupme_data['response']['messages']:
    date = datetime.fromtimestamp(a['created_at']).strftime('%c')
    groupme_table_data = (a['id'], ' '.join(date.split()[0:3]) + ', ' + date.split()[-1], date.split()[3], len(a['favorited_by']))
    cur.execute('INSERT INTO My_GroupMe_Messages (Message_ID, Date_of_Message, Time_of_Message, Number_of_Likes) VALUES (?, ?, ?, ?)', groupme_table_data)

#Instagam Table
cur.execute('DROP TABLE IF EXISTS My_Instagram_Posts')
cur.execute('CREATE TABLE My_Instagram_Posts (Post_ID TEXT, Date_Posted DATETIME, Time_Posted DATETIME, Number_of_Likes INTEGER, Number_of_Comments INTEGER, City_of_Post TEXT)')

insta_data = get_instagram_data()
insta_post_dict = {}
for a in insta_data['data']:
    post_data = []
    date = datetime.fromtimestamp(int(a['created_time'])).strftime('%c')
    if a['location'] == None:
        post_data = (date, a['likes']['count'], a['comments']['count'], 'No Location Given')
    else:
        post_data = (date, a['likes']['count'], a['comments']['count'], get_gmaps_data(str(a['location']['latitude']), str(a['location']['longitude'])))
    insta_post_dict[a['id']] = post_data

for b in insta_post_dict.items():
    insta_table_data = (b[0], ' '.join(b[1][0].split()[0:3]) + ', ' + b[1][0].split()[-1], b[1][0].split()[3], int(b[1][1]), int(b[1][2]), b[1][3])
    cur.execute('INSERT INTO My_Instagram_Posts (Post_ID, Date_Posted, Time_Posted, Number_of_Likes, Number_of_Comments, City_of_Post) VALUES (?, ?, ?, ?, ?, ?)', insta_table_data)

#Facebook Table
cur.execute('DROP TABLE IF EXISTS My_Facebook_Feed')
cur.execute('CREATE TABLE My_Facebook_Feed (Post_ID TEXT, User_Posted TEXT, Date_Posted DATETIME, Time_Posted DATETIME, Number_of_Likes, INTEGER, Number_of_Comments INTEGER)')

fb_data = get_facebook_data()
fb_post_dict = {}

for a in fb_data['data']:
    if 'likes' not in a or 'comments' not in a:
        post_data = (a['created_time'], 0, 0, a['from']['name'])
    else:
        post_data = (a['created_time'], len(a['likes']['data']), len(a['comments']['data']), a['from']['name'])
    fb_post_dict[a['id']] = post_data

for b in fb_post_dict.items():
    date = b[1][0].split('T')[0]
    formatted_date = date.replace('-', ' ')
    dt_object = datetime.strptime(date[:11], '%Y-%m-%d')
    day_of_week = calendar.day_name[dt_object.weekday()]
    fb_table_data = (b[0], b[1][3], str(day_of_week) + ', ' + date, str(b[1][0].split('T')[1][:8]), b[1][1], b[1][2])
    cur.execute('INSERT INTO My_Facebook_Feed(Post_ID, User_Posted, Date_Posted, Time_Posted, Number_of_Likes, Number_of_Comments) VALUES (?, ?, ?, ?, ?, ?)', fb_table_data)

#Email Table
cur.execute('DROP TABLE IF EXISTS UMich_Emails')
cur.execute('CREATE TABLE UMich_Emails (Subject_of_Email TEXT, Day_of_Email DATETIME, Time_of_Email DATETIME)')

gmail_data = get_gmail_data()

my_emails_dict = {}
subject = ''
frommm = ''
date = ''

for b in gmail_data:
    for c in b['payload']['headers']:
        if c['name'] == 'Subject':
            subject = c['value']
        elif c['name'] == 'From':
            frommm = c['value']
        elif c['name'] == 'Date':
            date = c['value']
        my_emails_dict[b['id']] = {'Subject': subject, 'From': frommm, 'Date': date}

for a in my_emails_dict.values():
    emails_table_data = (a['Subject'], ' '.join(a['Date'].split()[:4]), str(a['Date'].split()[4]))
    cur.execute('INSERT INTO Umich_Emails (Subject_of_Email, Day_of_Email, Time_of_Email) VALUES (?, ?, ?)', emails_table_data)

conn.commit()

# *** Prepping Visualization ***

def get_groupme_vis_data(data):
    groupme_table = cur.execute('SELECT Number_of_Likes, Date_of_Message FROM My_GroupMe_Messages')
    groupme_data = []
    for a in groupme_table:
        groupme_data.append(a)

    groupme_sum_likes = 0
    groupme_num_messages = 0
    groupme_times = {}
    for a in groupme_data:
        groupme_sum_likes += a[0]
        groupme_num_messages += 1
        if a[1][:3] not in groupme_times:
            groupme_times[a[1][:3]] = 0
        groupme_times[a[1][:3]] += 1


    if data == 'likes':
        return (groupme_sum_likes / groupme_num_messages)

    if data == 'times':
        return groupme_times

def get_facebook_vis_data(data):
    fb_table = cur.execute('SELECT Number_of_Likes, Date_Posted FROM My_Facebook_Feed')
    fb_data = []
    for a in fb_table:
        fb_data.append(a)

    fb_sum_likes = 0
    fb_num_posts = 0
    fb_times = {}
    for a in fb_data:
        fb_sum_likes += a[0]
        fb_num_posts += 1
        if a[1][:3] not in fb_times:
            fb_times[a[1][:3]] = 0
        fb_times[a[1][:3]] += 1


    if data == 'likes':
        return (fb_sum_likes / fb_num_posts)

    if data == 'times':
        return fb_times

def get_instagram_vis_data(data):
    ig_table = cur.execute('SELECT Number_of_Likes, Date_Posted FROM My_Instagram_Posts')
    ig_data = []
    for a in ig_table:
        ig_data.append(a)

    ig_sum_likes = 0
    ig_num_posts = 0
    ig_times = {}
    for a in ig_data:
        ig_sum_likes += a[0]
        ig_num_posts += 1
        if a[1][:3] not in ig_times:
            ig_times[a[1][:3]] = 0
        ig_times[a[1][:3]] += 1


    if data == 'likes':
        return (ig_sum_likes / ig_num_posts)

    if data == 'times':
        return ig_times

def get_gmail_vis_data():
    gmail_table = cur.execute('SELECT Day_of_Email FROM Umich_Emails')
    gmail_data = []
    for a in gmail_table:
        gmail_data.append(a)

    gmail_times = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0}
    for a in gmail_data:
        if a[0][0] == '1' or a[0][0] == '7':
            continue
        else:
            gmail_times[a[0][:3]] += 1

    return gmail_times

def get_map_visualization_data():
    map_data = []
    for a in insta_data['data']:
        if a['location'] != None:
            map_data.append(tuple([a['location']['latitude'], a['location']['longitude']]))
    return map_data

# *** Visualization ***
plotly.tools.set_credentials_file(username='jjvandal', api_key='mBPHHWrVLNJRR5Z30ezk') #set credentials for Plotly output

def recall(): #recall function for terminal output
    print('\n')
    print('What else do you want to see?')
    print('1. A table of Jack\'s Instagram, Facebook, and GroupMe Posts')
    print('2. A graph of Jack\'s University of Michigan Email Data')
    print('3. A map of locations from Jack\'s Instagram posts')
    return 'If done, type \'quit\' and press \'Enter\''

print('\n*** Welcome to Jack\'s Social Media Tracker Program! ***\n')
print('What would you like to see?\n')
print('1. A table of Jack\'s Instagram, Facebook, and GroupMe Posts')
print('2. A graph of Jack\'s University of Michigan Email Data')
print('3. A map of locations from Jack\'s Instagram posts')
print('If done, type \'quit\' and press \'Enter\'')
user_input = ''
#Terminal Output Interaction Page
while (user_input.lower() != 'quit'):
    user_input = input('> ')
    if user_input == '1':
        print('\n')
        print('Jack\'s Number of Posts/Messages Per Weekday')
        s1 = pd.DataFrame.from_dict([get_instagram_vis_data('times'), get_facebook_vis_data('times'), get_groupme_vis_data('times')])
        s1.index = ['Instagram', 'Facebook', 'GroupMe']
        print(s1)
        print('\n')
        print('Jack\'s Average Number of Likes per Post/Message')
        s2 = pd.DataFrame([get_instagram_vis_data('likes'), get_facebook_vis_data('likes'), get_groupme_vis_data('likes')])
        s2.index = ['Instagram', 'Facebook', 'GroupMe']
        s2.columns = ['Likes per Post/Message']
        print(s2)
        print(recall())

    elif user_input == '2':
        data = get_gmail_vis_data()
        x_axis = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        y_axis = [data['Mon'], data['Tue'], data['Wed'], data['Thu'], data['Fri'], data['Sat'], data['Sun']]
        data = [go.Bar(x=x_axis, y=y_axis)] #From example Plotly bar graph. Issue listed in references.
        layout = go.Layout(title = 'Jack\'s University of Michigan Emails', xaxis = dict(title = 'Day of Week'), yaxis = dict(title = 'Number of Emails')) #Lines ____-____ from basic tuturial of Plotly

        fig = go.Figure(data=data, layout=layout)
        py.plot(fig)
        print(recall())

    elif user_input == '3':
        data = get_map_visualization_data()
        world = Basemap(projection='mill',lon_0=-60, llcrnrlon= -150, llcrnrlat= -10, urcrnrlon= 60, urcrnrlat= 60)
        world.drawcoastlines()
        world.drawcountries()
        world.drawstates()
        world.drawparallels(np.arange(-70,70,30),labels=[1,0,0,0])
        world.drawmeridians(np.arange(world.lonmin,world.lonmax+40,60),labels=[0,0,0,1])
        world.drawmapboundary(fill_color='aqua')
        world.fillcontinents(color='green',lake_color='blue')
        for a in data:
            lon = a[1]
            lat = a[0]
            x,y = world(lon, lat)
            world.plot(x, y, 'r*', markersize=3)
        plt.title('Jack\'s Instagram Post Locations (Locations in Red)')
        plt.show()
        print(recall())
    elif user_input == 'quit':
        print('Have a nice day!')
    else:
        print('\nOops. Try entering that again.')
        print(recall())

cur.close()
