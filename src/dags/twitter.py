from requests import get
from airflow.models import Variable

import tweepy
import os

def get_authenticated_client() -> tweepy.API:
    api_key = Variable.get('api_key')
    api_key_secret = Variable.get('api_key_secret')
    access_token = Variable.get('access_token')
    access_token_secret = Variable.get('access_token_secret')
    
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)

    return tweepy.API(auth)

def tweet_random_card(card):
    client = get_authenticated_client()
    filename = 'card_image.png'

    with open(filename, 'wb') as handler:
        # Baixa a imagem
        handler.write(get(card['url'], allow_redirects=True).content)
        #Faz o tweet
        tweet_text = f'A carta aleatória de agora é: {card["@name"]}, com valor de ${card["price"]}'
        client.update_with_media(filename, tweet_text)
        #Exclui o arquivo da imagem
        os.remove(filename)

def tweet_best_card(card):
    client = get_authenticated_client()
    filename = 'card_image.png'

    with open(filename, 'wb') as handler:
        # Baixa a imagem
        handler.write(get(card['url'], allow_redirects=True).content)
        #Faz o tweet
        tweet_text = f'A carta mais cara de hoje foi: {card["name"]}, com valor de ${card["price"]}'
        client.update_with_media(filename, tweet_text)
        #Exclui o arquivo da imagem
        os.remove(filename)
