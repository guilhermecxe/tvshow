from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re
import socket

def getSoup(link:str):
    """ Given a link returns a BeautifulSoup instance """

    for i in range(3):
        try:
            resp = urlopen(link, timeout=15)
            return BeautifulSoup(resp.read(), 'lxml')
        except socket.timeout:
            continue
    
    raise Exception(f'Sorry, a timed out error was thrown 3 times for the link: {link}.')

def getSeasonRatings(tvshow_id:str, season:int):
    """ Given a tv show id (from imdb) and the number of a season, returns a list of the ratings of its episodes. """
    
    soup = getSoup(f'https://www.imdb.com/title/{tvshow_id}/episodes?season={season}')

    episodes = soup.find_all('div', {'itemprop': 'episodes'})
    ratings = []
    for ep in episodes:
        try:
            ratings.append(float(ep.find(class_='ipl-rating-star__rating').get_text()))
        except AttributeError: # When the rating for an episode is not found
            return ratings
    return ratings

def getSeasons(tvshow_id:str):
    """ Given a tv show id (from imdb), returns a list of the numbers of its seasons. """

    soup = getSoup(f'https://www.imdb.com/title/{tvshow_id}/episodes')

    seasons = soup.find(id='bySeason')
    seasons = set(int(option.get('value')) for option in seasons.find_all('option'))
    seasons.discard(-1)
    
    return seasons

def getTitle(tvshow_id:str):
    """ Given a tv show id (from imdb), returns its title. """

    soup = getSoup(f'https://www.imdb.com/title/{tvshow_id}')

    try:
        original_title = soup.find(class_=re.compile('OriginalTitle', flags=re.IGNORECASE)).get_text().split('title: ')[-1]
        return original_title.replace(' (original title)', '').strip()
    except: # When it don't has an original title, returns the main title
        return soup.find('h1').get_text().strip()

def getAllEpisodesRatings(tvshow_id:str):
    """ Given a tv show id (from imdb), returns a dataframe with all its episodes with seasons and ratings per episode. """
    
    seasons = []
    episodes = []
    ratings = []

    episode = 1
    for season in getSeasons(tvshow_id):
        for rating in getSeasonRatings(tvshow_id, season):
            seasons.append(season)
            episodes.append(episode)
            ratings.append(rating)
            episode += 1
    
    return pd.DataFrame({
        'season': seasons,
        'episode': episodes,
        'rating': ratings
    })