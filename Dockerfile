FROM ubuntu:latest
RUN apt-get update && apt-get upgrade -y && apt-get -y install python build-essential gunicorn python-dev python-pip libjpeg-dev libpng-dev jpegoptim python-dnspython
add . /app
RUN pip install -r /app/requirements.txt
ENV consulsuffix .service.dc1.consul
EXPOSE 5000
WORKDIR /app
CMD gunicorn -b :5000 run:app

