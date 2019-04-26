FROM ubuntu

MAINTAINER Abelardo Pardo

# Project Files and Settings
ENV PROJECT=ontask
ARG PROJECT=ontask
ARG PROJECT_DIR=/data/web
ENV PROJECT_DIR=${PROJECT_DIR}
ENV PROJECT_PATH=${PROJECT_DIR}
ENV CELERY_BIN=/usr/local/bin/celery
ENV PYTHONUNBUFFERED 1

# Set up packages
# Get pip and craeate the django project dir
RUN apt-get -yqq update && \
    apt-get install -yqq \
      curl \
      dialog \
      python3 \
      python3-pip \
      postgresql-client \
      libpq-dev \
      rsync \
      vim \
&& python3 -m pip install --no-cache-dir --upgrade pip \
&& mkdir -p $PROJECT_DIR

# Copy django project
WORKDIR $PROJECT_DIR
COPY . $PROJECT_DIR

# Install Requirements + supervisor
RUN python3 -m pip install --no-cache-dir --upgrade -r requirements/development.txt \
&& python3 -m pip install --no-cache-dir --upgrade supervisor

CMD ["/usr/local/bin/supervisord", "-n" ,"-c", "/data/web/supervisor/supervisor.conf"]
