import blaskr
from blaskr import models, db

blaskr.app.test_request_context().push()
db.drop_all()
db.create_all()

db.session.add(models.User("dmhathorn@gmail.com", "testtesttest", role= 1))
db.session.commit()
