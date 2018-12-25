#! /bin/bash
export FLASK_APP=app.main
export FLASK_ENV=development # switch this to production in production env!!
export OVERRIDE_CONF=config_override.yaml
flask run --host=127.0.0.1