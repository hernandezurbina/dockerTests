FROM ubuntu:16.04

# Install required packages and remove the apt packages cache when done.

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
	git \
	python3 \
	python3-dev \
	python3-setuptools \
	python3-pip \
	nginx \
  vim \
	supervisor \
	sqlite3 && \
	pip3 install -U pip setuptools && \
  rm -rf /var/lib/apt/lists/*

# install uwsgi now because it takes a little while
RUN pip3 install uwsgi

# install mysql tools
RUN apt-get update && \
  apt-get install -y libmysqlclient-dev && \
  pip3 install mysqlclient

# setup all the configfiles
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx-app.conf /etc/nginx/sites-available/default
COPY supervisor-app.conf /etc/supervisor/conf.d/

# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.

COPY requirements.txt /home/docker/code/myapp/
RUN pip3 install -r /home/docker/code/myapp/requirements.txt

# add (the rest of) our code
COPY . /home/docker/code/

# install django, normally you would remove this step because your project would already
# be installed in the code/app/ directory
# RUN django-admin.py startproject myapp /home/docker/code/

EXPOSE 80
CMD ["supervisord", "-n"]
