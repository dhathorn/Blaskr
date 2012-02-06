import monkey_patch
from helpers import populate_titletext
from blaskr.models import db
from flask import Flask, request, session, g, redirect, url_for, \
             abort, render_template, flash, Blueprint
from models import *
from forms import *
from login_manager import login_manager
from flaskext.login import current_user, login_user, login_required, logout_user

public = Blueprint('public', __name__)

#user views
@public.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter(User.email == form.email.data).first()
        login_user(user)
        flash("You were logged in")
        return redirect(url_for("public.index"))
    return render_template("public/login.html", form=form)

@public.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out")
    return redirect(url_for("public.index"))

@public.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        db.session.add(User(form.email.data, form.password.data))
        db.session.commit()
        flash("Account created")
        return redirect(url_for("public.login"))
    return render_template("public/register.html", form=form)

@public.route("/user/edit", methods=["GET", "POST"])
@login_required
def edit_user():
    user = current_user
    form = RegistrationForm(request.form, user)
    if request.method == "POST" and form.validate():
        form.populate_obj(user)
        db.session.commit()
        flash("Modification Successful")
    return render_template("public/edit.html", form=form)

#public post views
@public.route("/")
def index():
    entries = Post.query.order_by(Post.id.desc()).all()
    return render_template("show_entries.html", entries=entries)

@public.route("/posts/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(request.form)
    comment = CommentForm(post_id=post_id)
    if current_user.is_authenticated():
        del comment.recaptcha
    return render_template("show_post.html", post=post, comment=comment)

#comments
@public.route("/comments/add", methods=["POST"])
def add_comment():
    form = CommentForm(request.form)
    if current_user.is_authenticated():
        del form.recaptcha
    if request.method == "POST" and form.validate() and Post.query.get_or_403(form.post_id.data):
        db.session.add(Comment(form.title.data, form.text.data, form.post_id.data, session.get("user_id")))
        db.session.commit()
        flash("Successfully added comment! Woot!")
        return redirect(url_for("public.post", post_id=form.post_id.data))
    return render_template("show_post.html", post=Post.query.get(form.post_id.data), comment=form)

@public.route("/comments/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    form = CommentForm(request.form)
    post = Post.query.get(comment.post_id)
    if current_user.is_authenticated():
        del form.recaptcha
    if request.method == "POST":
        if not (current_user.is_authenticated() and comment.owner(current_user)):
            return login_manager.unauthorized()
        if form.validate():
            populate_titletext(form, comment)
            db.session.commit()
            flash("Successfully edited comment")
            return redirect(url_for("public.post", post_id = comment.post_id))
        elif form.method.data == "DELETE":
            db.session.delete(comment)
            db.session.commit()
            flash("Successfully deleted comment")
            return redirect(url_for("public.post", post_id=post.id))
        return render_template('edit_comment.html', comment = form)
    return render_template("show_comment.html", post=post, comment=comment)

@public.route('/comments/<int:comment_id>', methods=["GET", "POST"])
def comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return render_template('show_comment.html', post=Post.query.get(comment.post_id), comment=comment)
