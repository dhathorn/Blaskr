#imports
#from contextlib import closing
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.login import LoginManager
from models import db
from members_views import members

#config
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BLASKR_SETTINGS', silent=True)
app.secret_key ='\xac\r/\xe5\xd9\x94\xd1.\x14\xfd-\xb9I}\xdd;\x9a\x17E\xafM\x11/\xa1\xb8\x81z\xf1\xd5\xb5\xfdj/\xe43\x056\x82x\xed'
app.register_blueprint(members, url_prefix='/members')
db.init_app(app)

#flask-login
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"

import blaskr.views
