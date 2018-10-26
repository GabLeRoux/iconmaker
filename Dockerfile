FROM python:3.7.0

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y \
	imagemagick \
	icnsutils

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .
