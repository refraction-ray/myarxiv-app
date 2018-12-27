# MYARIXV-APP

A Flask web app written in Python 3. See the live demo at https://myarxiv.club (at the experimental stage)

## Quickstart

All commands below are executed in bash and the working directory is the root of the project.

* Run the app in development mode, `./run.sh` 

* Run the app in production mode, ` gunicorn -w 4 -b 0.0.0.0:9999 app.wsgi:app`

  For the above two options, you need to take care of dependencies. Try

  ```bash
  pip install -r requirements/prod.txt
  ```

  You also need to start celery worker and celery beat manually. 

  ```bash
  celery -A app.tasks worker --loglevel=info
  celery -A app.tasks beat --loglevel=info
  ```

* Run the flask app in docker (with database configured in the host). In this case, the host url for databases are recommended as `127.0.0.1` in config.yaml.

  ```bash
  docker build . -t myarxiv:latest
  docker run -d --network="host" myarxiv:latest
  ```

  For the above three options, you need to configure mysql and redis databases and their connections manually. In Ubuntu, try `apt install -y redis-server mysql-server libmysqlclient-dev` . 

* Run the flask app in docker (with both mysql and redis also in dockers). In this case, the host url are recommended as `mysql` and `redis` in config.yaml.

  ```bash
  docker-compose build
  docker-compose up -d
  ```

  For all the above options, Nginx can also be added and configured as the reverse proxy in production mode.


