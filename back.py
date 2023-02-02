import urllib3
import re
from bs4 import BeautifulSoup #pip install lxml(in order to work)

import requests

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# from ytinspector.youtube import YouTube
  
from youtubers_managing import *

from credentional import API_YT_KEY

EVIL_DB = get_connector()
BAD_COUNTRYs = ['ru','by']#BAD COUNTRY CODES

try:
    youtube = build('youtube', 'v3', developerKey=API_YT_KEY)
except Exception as e:
    print(e)

    
def get_banned_owners():
    cursor = EVIL_DB.cursor()
    cursor.execute("SELECT * FROM owners")
    return cursor.fetchall()

def get_banned_channels():
    cursor = EVIL_DB.cursor()
    cursor.execute("SELECT * FROM channels")
    return cursor.fetchall()


    
def get_youtube_id_and_country_from_video_url(video_url):
    # Extracts the YouTube video ID from the URL
    video_id = video_url.split('watch?v=')[1]

    # url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,recordingDetails&id={video_id}&key={API_YT_KEY}"
    
    # response = requests.get(url)
    response = youtube.search().list(
        part='snippet',
        q = video_id
    ).execute()
    # data = response.json()
    data = response
    country_code = "Unkown"
    try:
        country_code = data["items"][0]["recordingDetails"]["location"]["country"]
    except:
        # country_code = data["items"][0]["snippet"]["defaultAudioLanguage"]
        pass
    channel_id = data["items"][0]["snippet"]["channelId"]

    return channel_id,country_code
    
def get_yt_channels(description: str):#could be a name
    request = youtube.search().list(
        part='snippet',
        type='channel',
        q= description,
        maxResults=5
    )

    response = request.execute()
    channels = response['items']

    channels_ids = []
    for channel in channels:
        channels_ids.append((channel['id']['channelId']))

    return channels_ids



def get_youtube_id_by_channel_url(url):
    def get_youtube_id(url):
        return url.split('/')[-1]
    requests = youtube.search().list(
        part='snippet',
        type='channel',
        q = get_youtube_id(url)
    )
    response = requests.execute()
    channel = response['items'][0]
    return channel['id']['channelId']

def get_channel_info_by_url(url):
    youtube_id = get_youtube_id_by_channel_url(url)
    data = {"owner": "Unknown", "actions": "Unknown"}
    if is_channel_in_db_by_youtube_id(youtube_id):
        channel_id = get_channel_id(youtube_id)
        owner_name, action = get_channel_info(channel_id)
        data = {"owner": owner_name, "actions": action}
    return data
def get_yt_video_info(url):
    try:
        youtube_id, country_code = get_youtube_id_and_country_from_video_url(url)
    except:
        raise Exception("Wrong URL")
    data = {"owner": "Unknown", "actions": "Unknown"}
    if is_channel_in_db_by_youtube_id(youtube_id):
            channel_id = get_channel_id(youtube_id)
            owner_name, action = get_channel_info(channel_id)
            data = {"owner": owner_name, "actions": action}
        
    return data #return "" if channel is good
    

def get_youtubers_names_and_actions():
    raw_html = getHTMLtext('https://theylovewar.com/')
    raw_brands = raw_html.find_all('div',class_='brand')
    
    youtubers_infos = []
    for brand in raw_brands:
        social_classes = brand.find_all('i')
        #check if in social_links there is youtube class
        for i in social_classes:
            for j in i.get('class'):
                if 'youtube' in j:#find all of them(fa-youtube, fa_youtube-square)
                    raw_name = brand.find('div', class_ = 'name')
                    raw_action = brand.find('div', class_ = 'comment')
                    # print(raw_name.text, raw_action.text)
                    youtubers_infos.append((format_text(raw_name.text).lower(), format_text(raw_action.text))) #tuple of name and action
                    
    return youtubers_infos #list of tuples(name, action)


def getHTMLtext(url):#text version of HTML page
    http = urllib3.PoolManager()
    resp = http.request('GET', url)
    html_text = resp.data.decode('utf-8')
    soup = BeautifulSoup(html_text, 'lxml')
    return soup
    

def format_text(raw_text):
    text = re.sub(r'\s{2,}', ' ', raw_text)#remove all spaces greater than 1
    
    if text[0] == ' ':
        text = text[1:]
    if text[-1] == ' ':
        text = text[:-1]
    
    return text

def update_db_from_web():
    youtubers_infos = get_youtubers_names_and_actions()
    failed = []
    for youtuber_info in youtubers_infos:
        name = youtuber_info[0]
        comment = youtuber_info[1]
        if not is_owner_in_db_by_name(name):
            channels_ids = get_yt_channels(name)
            for channel_id in channels_ids:
                try:
                    add_owner_to_db(name, comment, channel_id)
                except NameError as error:
                    failed.append(f"{name}: {error}")
        else:
            failed.append(f"{name}: already in db")
    return failed
        
# print(update_db_from_web())
