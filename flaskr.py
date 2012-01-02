#imports
from flaskext.sqlalchemy import SQLAlchemy
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
             abort, render_template, flash

#app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/flaskr.db'
db = SQLAlchemy(app)

#models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.String(180))

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return '<Title %r>' % self.title

#routes
@app.route('/')
def show_entries():
    entries = Post.query.order_by(Post.id.desc()).all()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db.session.add(Post(request.form['title'], request.form['text']))
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
