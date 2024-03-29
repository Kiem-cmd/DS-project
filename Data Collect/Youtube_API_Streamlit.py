import pandas as pd
import numpy as np
import streamlit as st 
from googleapiclient.discovery import build 
from datetime import datetime
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(page_title="My Streamlit App", page_icon=":guardsman:", layout="wide", initial_sidebar_state="expanded")


api_service_name = "youtube"
api_vesion = "v3"
api_key = "AIzaSyDCqxnfBlt3HAK7XzRCKfJ6IY3stnC7HOY"
youtube = build(api_service_name, api_vesion,developerKey=api_key)
def get_channel_id(custom_URL):
    request = youtube.search().list(
        part="id",
        q=custom_URL,
        type="channel"
    )
    response = request.execute()
    return response['items'][0]['id']['channelId']

def channel_statistic(channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id = channel_id
    )
    response = request.execute()
    date = response['items'][0]['snippet']['publishedAt']
    date_time_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    data = date_time_obj.strftime("%d-%m-%Y")
    channel_data = {
        'Name_Channel': [response['items'][0]['snippet']['localized']['title']],
        'Date of Publish':[data],
        'Country' : [response['items'][0]['snippet']['country']],
        'Subcriber':[response['items'][0]['statistics']['subscriberCount']],
        'Video_Count':[response['items'][0]['statistics']['videoCount']],
        'View_Count':[response['items'][0]['statistics']['viewCount']]      
    }
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    df = pd.DataFrame(channel_data)
    return df,playlist_id
def get_video_id(playlist_id):
    video_ids = []
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId = playlist_id,
        maxResults = 50
    )
    response = request.execute()
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
    next_page_token = response.get('nextPageToken')
    more_pages = True
    while more_pages:           
        if (next_page_token is None):
            more_pages = False 
        else:
            request = youtube.playlistItems().list(
                part = 'contentDetails',
                playlistId = playlist_id,
                maxResults = 50,
                pageToken = next_page_token
            )
            response = request.execute()
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            next_page_token = response.get('nextPageToken')
    return video_ids
def video_statistic(video_id):
    request = youtube.videos().list(
    part="snippet,contentDetails,statistics",
    id=video_id)
    response = request.execute()
    date = response['items'][0]['snippet']['publishedAt']
    date_time_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    data = date_time_obj.strftime("%d-%m-%Y")
    video_data = {
    'Title' : [response['items'][0]['snippet']['localized']['title']],
    'Publish At':[data],
    'View Count' : [response['items'][0]['statistics']['viewCount']],
    'Like Count' : [response['items'][0]['statistics']['likeCount']],
    'Comment Count' : [response['items'][0]['statistics']['commentCount']]
    }
    return video_data

    
st.header("Channel ID")
custom_URL= st.text_input("",max_chars=2000)

if custom_URL:
    channel_id = get_channel_id(custom_URL)
    df,playlist_id = channel_statistic(channel_id)
    st.subheader("Channel Statistic")
    st.dataframe(df,width=2000)

    video_ids  = get_video_id(playlist_id)

    st.subheader("Video Statistic")
    video_data = []
    for i in video_ids:
        video_data.append(video_statistic(i))
    df = pd.DataFrame(video_data)
    df['Month'] = [df['Publish At'][i][0][3:] for i in range(len(df))]
    df['Month'] = pd.to_datetime(df['Month'], format='%m-%Y')
    df['View Count'] = [int(df['View Count'][i][0]) for i in range(len(df))]
    df = df.sort_values('Month')
    a = df.groupby('Month')['View Count'].sum()
    df_view = a.reset_index()
    df_view = df_view.set_index('Month')
    df_video = df.groupby('Month')['Title'].count().reset_index()
    df_video = df_video.sort_values('Month')
    df_video = df_video.set_index('Month')
    st.subheader("Video Count")
    st.line_chart(df_video)
    # Display the chart using Streamlit
    st.subheader("View Count")
    st.line_chart(df_view)
    

    st.dataframe(df)
    
