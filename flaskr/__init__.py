#imports
#from contextlib import closing
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

def init_db(app): 
    "This function is exported so we can create databases in test"
    return SQLAlchemy(app)

#config
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.secret_key ='\xac\r/\xe5\xd9\x94\xd1.\x14\xfd-\xb9I}\xdd;\x9a\x17E\xafM\x11/\xa1\xb8\x81z\xf1\xd5\xb5\xfdj/\xe43\x056\x82x\xed'
db = init_db(app)


import flaskr.views
