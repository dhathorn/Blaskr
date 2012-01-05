from flaskr import app, db
from flask import Flask, request, session, g, redirect, url_for, \
             abort, render_template, flash
from models import *
from forms import *

#views
@app.route("/")
def show_entries():
    entries = Post.query.order_by(Post.id.desc()).all()
    return render_template("show_entries.html", entries=entries, form=PostForm())

@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = Post.query.filter(Post.id == post_id).first()
    return render_template("post.html", post=post)

@app.route("/post/edit/<int:post_id>")
def edit_post(post_id):
    post = Post.query.filter(Post.id == post_id).first()
    raise notimplimentederror()

@app.route("/post/add", methods=["GET", "POST"])
def add_post():
    if not session.get("email"):
        abort(401)
    form = PostForm(request.form)
    if request.method == "POST" and form.validate():
        db.session.add(Post(form.title.data, form.text.data))
        db.session.commit()
        flash("New entry was successfully posted")
        return redirect(url_for("show_entries"))
    return render_template("add_post.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        session["email"] = form.email.data
        flash("You were logged in")
        return redirect(url_for("show_entries"))
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    flash("You were logged out")
    return redirect(url_for("show_entries"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        db.session.add(User(form.email.data, form.password.data))
        db.session.commit()
        flash("Account Created")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    user = User.query.filter(User.email == session["email"]).first()
    if not user:
        return redirect(url_for("login"))

    form = RegistrationForm(request.form, user)
    if request.method == "POST" and form.validate():
        form.populate_obj(user)
        db.session.commit()
        flash("Modification Successful")
    return render_template("edit.html", form=form)

@app.route("/comment/add/<int:post_id>", methods=["POST"])
def add_comment():



