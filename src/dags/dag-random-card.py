from requests import get, Response

from dataclasses import dataclass, asdict

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago
import tweepy
import os


@dataclass
class Card:
    name: str
    url: str
    price: float


def get_random_card() -> Card:
    response: Response = get('https://api.scryfall.com/cards/random')
    card_data: dict = response.json()

    return Card(
        name=card_data['name'],
        url=card_data['image_uris']['png'],
        price=float(card_data['prices']['usd'] or 0)
    )


def print_card_info(card: Card):
    print(f'🎲 Your random card was: {card.name}!')
    print(f'💰 The current price is: {card.price}.')
    print(f'👇 You can download the image here: {card.url}')


def get_authenticated_client() -> tweepy.API:
    api_key = Variable.get('api_key')
    api_key_secret = Variable.get('api_key_secret')
    access_token = Variable.get('access_token')
    access_token_secret = Variable.get('access_token_secret')
    
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)

    return tweepy.API(auth)

def tweet_card(card: Card):
    client = get_authenticated_client()
    filename = 'card_image.png'
    
    with open(filename, 'wb') as handler:
        # Baixa a imagem
        handler.write(get(card.url, allow_redirects=True).content)
        #Faz o tweet
        tweet_text = f'A carta aleatória de agora é: {card.name}, com valor de ${card.price}'
        client.update_with_media(filename, tweet_text)
        #Exclui o arquivo da imagem
        os.remove(filename)


with DAG(
    dag_id='random_card_dag',
    default_args=dict(retries=3, start_date=days_ago(7)),
    schedule_interval='0 * * * *',
    catchup=False
) as dag:
    start = DummyOperator(task_id='Start')

    card = get_random_card()

    print_card_info = PythonOperator(
        task_id='show_random_card_info',
        python_callable=print_card_info,
        op_args=[card],
    )

    create_table_cards = PostgresOperator(
        task_id='create-table-cards',
        sql="sql/create-table-cards.sql"
    )

    insert_card = get_birth_date = PostgresOperator(
        task_id="insert-card",
        sql="sql/insert-card.sql",
        params=asdict(card),
    )

    tweet = PythonOperator(
        task_id='tweet',
        python_callable=tweet_card,
        op_args=[card]
    )


    end = DummyOperator(task_id='End')

    start >> print_card_info >> create_table_cards >> insert_card >> tweet >>end
