# import external libraries
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
# import database
from . import db
# import from .models user
from .models import Post

#set views blueprint
views = Blueprint("views", __name__)

# default / home route
@views.route("/")
@views.route("/home")
# home route function
# returns home.html
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)


# create blog post route
@views.route("/create-post", methods=['GET', 'POST'])
# user must be logged in to post
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        if not title:
            flash('Title cannot be empty', category='error')
        elif not content:
            flash('Blog cannot be empty', category='error')
        else:
            post = Post(title=title, content=content, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("create_post.html", user=current_user)