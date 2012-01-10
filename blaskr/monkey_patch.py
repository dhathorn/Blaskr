import flaskext
from flask import abort

def get_or_403(self, primary_key):
    return self.get(primary_key) or abort(403)

#monkey patching time!
flaskext.sqlalchemy.BaseQuery.get_or_403 = get_or_403
