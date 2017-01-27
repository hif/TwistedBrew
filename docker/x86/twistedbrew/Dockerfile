FROM python:3-alpine

RUN apk add --no-cache g++ musl-dev

ENV DJANGO_SETTINGS_MODULE twisted_brew.settings
ENV PROJECT_DIR /twisted_brew

COPY . ${PROJECT_DIR}
WORKDIR ${PROJECT_DIR}

RUN pip install -r requirements.txt

VOLUME ${PROJECT_DIR}/database
# RUN python manage.py syncdb --noinput

CMD ["python","-u","manage.py","twisted_brew","./config/twisted_brew.yml"]

