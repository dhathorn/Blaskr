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
    return render_template("members/show_entries.html", entries=entries, form=PostForm())

@members.route("/posts")
def posts_index():
    entries = Post.query.order_by(Post.id.desc()).all()
    return render_template("members/show_entries.html", entries=entries, form=PostForm())

@members.route("/posts/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comment = CommentForm(post_id=post_id)
    return render_template("members/show_post.html", post=post, comment=comment)

@members.route("/posts/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(request.form, post, post_id=post_id)
    if request.method == "POST":
        if not post.owner(current_user):
            not_authorized()
        if form.validate():
            if form.delete.data:
                db.session.delete(post)
                db.session.commit()
                flash("Successfully deleted post")
                return redirect(url_for("members.index"))
            else:
                populate_titletext(form, post)
                db.session.commit()
                flash("Successfully edited post")
                return redirect(url_for("members.post", post_id=post_id))
    return render_template("members/edit_post.html", post=form)


@members.route("/posts/add", methods=["GET", "POST"])
def add_post():
    form = PostForm(request.form)
    if request.method == "POST" and form.validate():
        db.session.add(Post(form.title.data, form.text.data, session["user_id"]))
        db.session.commit()
        flash("New entry was successfully posted")
        return redirect(url_for("members.index"))
    return render_template("members/add_post.html", form=form)
#comments
@members.route("/comment/add", methods=["POST"])
def add_comment():
    form = CommentForm(request.form)
    if current_user.is_authenticated():
        del form.recaptcha
    if request.method == "POST" and form.validate() and Post.query.get_or_403(form.post_id.data):
        db.session.add(Comment(form.title.data, form.text.data, form.post_id.data, session.get("user_id")))
        db.session.commit()
        flash("Successfully added comment! Woot!")
        return redirect(url_for("public.show_post", post_id=form.post_id.data))
    return render_template("show_post.html", post=Post.query.get(form.post_id.data), comment=form)

@members.route("/comment/<int:comment_id>", methods=["GET", "POST"])
def comment(comment_id):
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
            return redirect(url_for("members.post", post_id = comment.post_id))
        elif form.method.data == "DELETE":
            db.session.delete(comment)
            db.session.commit()
            flash("Successfully deleted comment")
            return redirect(url_for("members.post", post_id=post.id))
        #needs an edit comment template
    return render_template("public/show_comment.html", post=Post.query.get(comment.post_id), comment=comment)

