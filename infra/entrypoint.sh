#!/bin/bash

airflow db init
airflow users create --username admin --password admin --role Admin --firstname admin --lastname admin --email admin@email.com
airflow scheduler & 
sleep 5
airflow webserver