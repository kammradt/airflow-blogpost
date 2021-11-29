from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago

from twitter import tweet_card

with DAG(
    dag_id='dag_card_of_the_day',
    default_args=dict(retries=3, start_date=days_ago(7)),
    schedule_interval='50 23 * * *',
    catchup=False
) as dag:
    start = DummyOperator(task_id='Start')

    postgres_hook = PostgresHook()
    results = postgres_hook.get_records(
        sql="select name, price, url from cards order by price desc limit 1;",
    )
    name, price, url = results[0]
    card = dict(name=name, price=price, url=url)

    tweet = PythonOperator(
        task_id='tweet',
        python_callable=tweet_card,
        op_args=[card]
    )

    end = DummyOperator(task_id='End')

    start >> tweet >>end
