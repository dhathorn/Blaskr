#imports
#from contextlib import closing
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from login_manager import login_manager
from models import db
from members_views import members
from public_views import public

#config
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('BLASKR_SETTINGS', silent=True)
app.secret_key ='\xac\r/\xe5\xd9\x94\xd1.\x14\xfd-\xb9I}\xdd;\x9a\x17E\xafM\x11/\xa1\xb8\x81z\xf1\xd5\xb5\xfdj/\xe43\x056\x82x\xed'
app.register_blueprint(members, url_prefix='/members', template_folder="members_templates")
app.register_blueprint(public, template_folder="public_templates")
db.init_app(app)
login_manager.setup_app(app)

import blaskr.public_views
import blaskr.members_views
