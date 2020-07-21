FROM jenkins:latest
USER root
RUN mkdir taxi_app
WORKDIR /taxi_app
COPY requirements.txt /taxi_app
RUN pwd
RUN ls -la
RUN apt-get update
RUN apt-get install -y python.pip