FROM python:3.9-alpine

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
