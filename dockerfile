FROM python:3.6
LABEL author="refraction-ray"

COPY requirements.txt /
RUN pip install -r /requirements.txt
RUN pip install gunicorn eventlet

RUN apt update && apt install -y supervisor

COPY app /www/app/
COPY supervisor /www/supervisor/

WORKDIR /www
RUN mkdir log
RUN cp /usr/share/zoneinfo/Hongkong /etc/localtime

CMD ["/usr/bin/supervisord", "-c", "supervisor/supervisord.conf"]
