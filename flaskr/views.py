import monkey_patch
from helpers import populate_comment
from flaskr import app, db, login_manager
from flask import Flask, request, session, g, redirect, url_for, \
             abort, render_template, flash
from models import *
from forms import *
from flaskext.login import current_user, login_user

#views

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        flash("You were logged in")
        login_user(User.query.filter(User.email == form.email.data).first()) 
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
        flash("Account created")
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

@app.route("/")
def show_entries():
    entries = Post.query.order_by(Post.id.desc()).all()
    return render_template("show_entries.html", entries=entries, form=PostForm())

@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("show_post.html", post=post, comment=CommentForm(post_id=post_id))

@app.route("/post/edit/<int:post_id>")
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
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

#comments
@app.route("/comment/add", methods=["POST"])
def add_comment():
    form = CommentForm(request.form)
    if request.method == "POST" and form.validate() and Post.query.get_or_403(form.post_id.data):
        db.session.add(Comment(form.title.data, form.text.data, form.post_id.data))
        db.session.commit()
        flash("Successfully added comment! Woot!")
        return redirect(url_for("show_post", post_id=form.post_id.data))
    else:
        return render_template("show_post.html", post=Post.query.filter(Post.id == form.post_id.data).first(), comment=form)

@app.route("/comment/<int:comment_id>", methods=["GET", "POST"])
def comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    form = CommentForm(request.form)
    post = Post.query.get(comment.post_id)
    if request.method == "POST":
        if form.validate():
            populate_comment(form, comment)
            db.session.commit()
            flash("Successfully edited comment")
            return redirect(url_for("show_post", post_id = comment.post_id))
        elif form.method.data == "DELETE":
            db.session.delete(comment)
            db.session.commit()
            flash("Successfully deleted comment")
            return redirect(url_for("show_post", post_id=post.id))
    return render_template("show_comment.html", post=Post.query.get(comment.post_id), comment=form)

#login
@login_manager.user_loader
def load_user(userid):
    User.query.get(userid)
