import googleapiclient.errors
import googleapiclient.discovery
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from googleapiclient.discovery import build
import subprocess
from pytube import YouTube
from pytube import Playlist
import os
import sys
import re
from pathlib import Path
from moviepy.editor import *
import asyncio
from threading import Thread
import threading

file_path = os.path.dirname(__file__)
module_path = os.path.join(file_path, "lib")
sys.path.append(module_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "causal-inquiry-291406-4a7535d9d7f5.json"
apiKey = 'AIzaSyAWPJqklF9tnOMax7ho1XvOOjIFFR1h6WQ'

#request = youtube.c
# ...
# service.close()


# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlists.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def convert(vid, i, countElements, _playlist):
    default_filename = Path(vid)
    new_filename = Path(vid.replace('mp4', 'mp3'))
    video = AudioFileClip(os.path.join(default_filename))
    video.write_audiofile(os.path.join(new_filename))
    video.close()
    os.remove(default_filename)
    print(str(i) + '/' + str(countElements) + ' converted in playlist with name of ' + _playlist['snippet']['title'])
    pass


async def download(_playlist, dir, url, i, countElements):
    vid = ''
    try:
        vid = YouTube(url).streams.get_audio_only().download(dir + '/' + _playlist['snippet']['title'])
        print(str(i) + '/' + str(countElements) + ' downloaded in playlist with name of ' + _playlist['snippet']['title'])
        convert(vid, i, countElements, _playlist)
    except:
        try:
            vid = YouTube(url).streams.get_audio_only().download(dir + '/' + _playlist['snippet']['title'])
            print(str(i) + '/' + str(countElements) + ' downloaded')
            convert(vid, i, countElements, _playlist)
        except:
            print('Error in ' + str(i) + '/' + str(countElements) + ' in playlist with name of ' + _playlist['snippet']['title'])
    pass


def playlist(_playlist, dir):
    playlist = Playlist(
        'https://www.youtube.com/playlist?list=' + _playlist['id'])
    countElements = len(playlist.video_urls)
    print('Number of videos in playlist with name of ' +
        _playlist['snippet']['title'] + ': %s' % countElements)
    if not os.path.isdir(dir + '/' + _playlist['snippet']['title']):
        os.mkdir(dir + '/' + _playlist['snippet']['title'])

    i = 0
    for url in playlist:
        i += 1
        asyncio.run(download(_playlist, dir, url, i, countElements))

        #download(_playlist, dir, url, i, countElements)
        #asyncio.create_task(download(_playlist, dir, url, i, countElements))
    pass

def main():

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    client_secrets_file = "client_secret_web_client.apps.googleusercontent.com.json"

    # Get credentials and create an API client
    #flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    #    client_secrets_file, scopes)
    #credentials = flow.run_local_server(port=5000, prompt='consent')

    credentials = None

    # token.pickle stores the user's credentials from previously successful logins
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_web_client.apps.googleusercontent.com.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube.readonly'
                ]
            )

            flow.run_local_server(port=5000, prompt='consent',
                                authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)


    youtube = build(
        'youtube', 'v3', credentials=credentials)
    #youtube = build('youtube', 'v3', developerKey=apiKey)

    request = youtube.playlists().list(
        part="snippet,contentDetails",
        mine='true',
        maxResults=25
    )
    response = request.execute()

    # print(response['items'][0]['id'])
    dir = 'D:/Downloads'
    if not os.path.isdir(dir):
        os.mkdir(dir)

    downloadAll = input('Choose one: Download all (type \'all\') or Select manually (type \'m\' or whatever): ')
    threads=[]
    for _playlist in response['items']:
        if downloadAll == 'all' or input('Do you want download playlist with name ' + _playlist['snippet']['title'] + ' (y/n): ') == 'y': threads.append(Thread(target=playlist, args=(_playlist, dir, )))

    for thread in threads: 
        thread.start()

            #subprocess.run([
            #    'ffmpeg',
             #   '-i', default_filename,
              #  new_filename
            #])
            #print(str(i) + '/' + str(countElements) + ' coverted')
    # playlist.download_all()
    pass


if __name__ == "__main__":
    main()
