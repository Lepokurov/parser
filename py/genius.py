from time import sleep

from bs4 import BeautifulSoup
import requests as req
url_genius = 'https://genius.com/'
url_artist = 'artists/'
url_song_end = '-lyrics'


def request_construct_song_upg(url_req):
    resp = req.get(url_genius + url_req + url_song_end)
    img = False
    youtube = False
    if resp.status_code == 404:
        return img, youtube
    soup = BeautifulSoup(resp.text, 'lxml')
    try:
        img = str(soup).split('&quot;custom_song_art_image_url&quot;:&quot;')[1].split('&quot;')[0]
    except:
        try:
            img = str(soup).split('<img class="SizedImage__NoScript-sc-1hyeaua-1 hYJUSb" src="')[1].split('"')[0]
        except:
            img = str(soup).split('https://images.genius.com/')[1].split('"')[0]
            img = 'https://images.genius.com/' + img
    try:
        youtube = str(soup).split('http://www.youtube.com/watch?v=')[1].split('&')[0]
        if len(youtube) > 15:
            youtube = youtube.split('\\')[0]
        youtube = 'http://www.youtube.com/watch?v=' + youtube
    except:
        youtube = False
    return img, youtube

while True:
    img, youtube = request_construct_song_upg('Nicki-minaj-only')
    print(img+' _______')
    #print()
    #print()
    #print(str(youtube))
    #print('------------------------------------')
    #a = int(input())