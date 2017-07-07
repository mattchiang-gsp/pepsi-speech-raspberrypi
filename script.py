#!/usr/bin/env python

from __future__ import unicode_literals
import glob
import os
import pygame

# Speech recognition
import speech_recognition as sr

# Spotify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Youtube
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import youtube_dl

# Set the Spotify and Youtube API keys
SPOTIPY_CLIENT_ID = '520f7611720a44199d2db42fa6044f90'
SPOTIPY_CLIENT_SECRET = 'd5005ef93dff4791978bd93f3abbb376'
client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

DEVELOPER_KEY = "AIzaSyA_5__FkmspfXLvOqajSVohXaBm_PZnXvE"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }],
}

### 

# Grab track from a spotify playlist
# TODO: Change playlist selection based on speech sentiment
def get_title_and_artist():
    # Grilling and Chilling playlist spotify:user:spotify:playlist:37i9dQZF1DXaajrW2mmprj
    playlist = sp.user_playlist('spotify', 'spotify:user:spotify:playlist:37i9dQZF1DXaajrW2mmprj')

    # Get the title and artist of the first track in the playlist for now
    title = playlist['tracks']['items'][0]['track']['name']
    artist = playlist['tracks']['items'][0]['track']['artists'][0]['name'] 
    print(playlist['tracks']['items'][0]['track']['name'])
    print(playlist['tracks']['items'][0]['track']['artists'][0]['name'])

    return title + " " + artist

# Search for the list of youtube videos based off the randomly selected spotify track
# Doesn't result in all videos like official Topic/Vevo for some reason
def youtube_search(search_term):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Call search.list method to retrieve results matching the specified query term
    search_response = youtube.search().list(
        q=search_term,
        part="id",
        maxResults=1,
        type="video"
    ).execute()

    videos= []

    # Add videos to list and display the list
    for search_result in search_response.get("items", []):
        videos.append("%s" % (search_result["id"]["videoId"]))

    print(videos)

    return videos

# Extract audio only from youtube video
def download_yt_audio(video_id):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # ydl.download(['https://www.youtube.com/watch?v=' + video_id])
        ydl.download(['https://www.youtube.com/watch?v=O5mcLhuUfG0'])

# Define trigger words to actually play a song
def said_trigger_words(value):
    if "pepsi" in value.lower():
        return True
    return False

# Fetch a track from spotify based on speech input
# TODO: Currently keyword trigger is "I feel {whatever_user_says_next}"
def play_song(speech_input):
    def fetch_song(speech_input):    
        try:
            # Grab a track's title and artist and from a specific Spotify playlist based on what was said
            title_and_artist = get_title_and_artist()

            # Use the title and artist to search for the YouTube video and then extract audio
            video_id_result = youtube_search(title_and_artist)[0]
            download_yt_audio(video_id_result)

            current_working_directory = os.getcwd()
            os.chdir(current_working_directory)
            for file in glob.glob('*.wav'):
                the_wav = file
            return the_wav
        except (HttpError, e):
            print("An HTTP error %d occured:\n%s" % (e.resp.status, e.content))

    pygame.mixer.init(frequency=48000)
    # Play smooth tone, then play despacito
    if speech_input == "fail":
        pygame.mixer.music.load('fail.wav')
        pygame.mixer.music.play()
    else:
        pygame.mixer.music.load('drop-bieber.wav')
        pygame.mixer.music.play()

    # pygame.mixer.music.load(fetch_song(speech_input))
    # if 'chill' in speech_input:
    #     os.system("echo 'alright dude, lets chill out'")
    #     os.system("say 'alright dude, lets chill out'")
    #     pygame.mixer.music.load('8Ee4QjCEHHc.wav')
    # elif 'flavor' in speech_input:
    #     os.system("echo 'alright dude, lets add some flavor to this party'")
    #     os.system("say 'alright dude, lets add some flavor to this party'")        
    #     pygame.mixer.music.load('Fi8rsCncwF8.wav')
    # elif 'spice' in speech_input:
    #     os.system("echo 'alright dude, its about to get spicy'")
    #     os.system("say 'alright dude, its about to get spicy'")        
    #     pygame.mixer.music.load('If27FnxvjZA.wav')
    # elif 'turn up' in speech_input:
    #     os.system("echo 'thats what im talking about'")
    #     os.system("say 'thats what im talking about'")        
    #     pygame.mixer.music.load('Qq-n0Hqg4Ik.wav')

    # pygame.mixer.music.play()

def main():
    # 1. Initialize speech recognition
    try:
        # Obtain audio from the microphone
        # May need to reconfigure for RaspberryPi
        r = sr.Recognizer()
        m = sr.Microphone()
        print("A moment of silence for the mic to start...")
        with m as source:
            while True:
                # Run into problem where it's catching the audio playing
                # So getting another mic command in is hard
                r.adjust_for_ambient_noise(source)
                print("Set minimum energy threshold to {}".format(r.energy_threshold))
                print("Say something now!")
                # with m as source: audio = r.listen(source)
                audio = r.listen(source)
                print ("Got it! Now recognizing what you said...")
                try:
                    # recognize speech using Google Speech Recognition
                    value = r.recognize_google(audio)

                    # we need some special handling here to correclty print unicode characters to standard output
                    if str is bytes: # Python2 uses bytes for strings
                        print(u"You said: {}".format(value).encode("utf-8"))
                    else: # Python3+ uses unicode for strings
                        print("You said {}".format(value))

                    # 2. Use speech result as input to play a song
                    # Only if certain words are recognized
                    if said_trigger_words(value):
                        play_song(value)
                    # else:
                    #     play_song("fail")


                except sr.UnknownValueError:
                    print("Oops! Didn't recognize what you just said")
                except sr.RequestError as e:
                    print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
    except KeyboardInterrupt:
        pass
    

if __name__ == '__main__':
    main()
