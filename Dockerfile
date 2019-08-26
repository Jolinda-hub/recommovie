FROM python:3.6-slim

# make directory in tmp
RUN mkdir -p /tmp/recommovie

# copy project to tmp
COPY . /tmp/recommovie/

# set working directory
WORKDIR /tmp/recommovie

# install curl fo testing from container
RUN apt-get update && apt-get -y install curl

# upgrade pip
RUN pip3 install --upgrade pip

# install required packages
RUN pip3 install -r requirements.txt

# app port
EXPOSE 5002

# run code
ENTRYPOINT python3 main.py config.ini
