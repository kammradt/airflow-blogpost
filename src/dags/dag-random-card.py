from requests import get, Response

from dataclasses import dataclass, asdict

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago


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


with DAG(
    dag_id='random_card_dag',
    default_args=dict(retries=3, start_date=days_ago(7)),
    schedule_interval=None,
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
        sql='''
            create table if not exists cards
            (
                id serial constraint cards_pk primary key,
                name text not null,
                url text not null,
                price float not null
            );
            '''
    )

    insert_card = get_birth_date = PostgresOperator(
        task_id="insert-card",
        sql="insert into cards ( name, url, price) values (%(name)s, %(url)s, %(price)s);",
        parameters=asdict(card),
    )

    end = DummyOperator(task_id='End')

    start >> print_card_info >> create_table_cards >> insert_card >> end