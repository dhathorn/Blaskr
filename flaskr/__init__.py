#imports
#from contextlib import closing
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

#app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
db = SQLAlchemy(app)

import flaskr.views

if __name__ == '__main__':
    app.run(host='0.0.0.0')
