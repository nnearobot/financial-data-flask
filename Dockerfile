FROM python:3.8-slim

RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential
    
RUN pip3 install --no-cache-dir pipenv
RUN pip3 install uWSGI

WORKDIR /srv/financial_api

COPY Pipfile Pipfile.lock uwsgi.ini start.sh ./

COPY financial ./financial
COPY get_raw_data.py ./
COPY .env.production ./.env

COPY nginx.conf /etc/nginx/

RUN pipenv install --system --deploy

EXPOSE 80

ENTRYPOINT ["/srv/financial_api/start.sh"]
