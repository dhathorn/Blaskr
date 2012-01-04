from flaskr import app, db
from flask import Flask, request, session, g, redirect, url_for, \
             abort, render_template, flash
from models import *
from forms import *

#views
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
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        session['logged_in'] = True
        flash('You were logged in')
        return redirect(url_for('show_entries'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        db.session.add(User(form.email.data, form.password.data))
        db.session.commit()
        flash('Account Created')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
