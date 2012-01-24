from flask import Blueprint, render_template, url_for, flash, abort, request,\
                    redirect
from flaskext.login import current_user, login_required
from models import Post, User, Comment, db
from forms import *
from helpers import populate_titletext

members = Blueprint('members', __name__)

def not_authorized():
    abort(401) #FIXME make this more user friendly

@members.before_request
@login_required
def member_auth():
    if not current_user.is_authorized("Member"):
        return not_authorized()

@members.route("/")
def index():
    entries = Post.query.order_by(Post.id.desc()).all()
    return render_template("show_entries.html", entries=entries, form=PostForm())

@members.route("/posts")
def posts_index():
    entries = Post.query.order_by(Post.id.desc()).all()
    return render_template("show_entries.html", entries=entries, form=PostForm())

@members.route("/posts/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(request.form)
    if request.method == "POST":
        if not post.owner(current_user):
            not_authorized()
        if form.validate():
            populate_titletext(form, post)
            db.session.commit()
            flash("Successfully edited post")
        elif form.method.data == "DELETE":
            db.session.delete(post)
            db.session.commit()
            flash("Successfully deleted post")
            return redirect(url_for("members.index"))
        #needs an edit post template

    comment = CommentForm(post_id=post_id)
    if current_user.is_authenticated():
        del comment.recaptcha
    return render_template("show_post.html", post=post, comment=comment, comments=post.comments.all())

@members.route("/posts/add", methods=["GET", "POST"])
def add_post():
    form = PostForm(request.form)
    if request.method == "POST" and form.validate():
        db.session.add(Post(form.title.data, form.text.data, session["user_id"]))
        db.session.commit()
        flash("New entry was successfully posted")
        return redirect(url_for("members.index"))
    return render_template("members/add_post.html", form=form)
