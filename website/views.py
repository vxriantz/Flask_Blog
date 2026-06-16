
# import external libraries
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date, timedelta

# import database
from . import db

# import from .models user
from .models import User, Post, Comment, Like, Appointment

# import from .forms
from .forms import PostForm, UserPermissionUpdateForm

#set views blueprint
views = Blueprint("views", __name__)


# default / home route
@views.route("/")
@views.route("/home")
# home route function
# returns home.html
def home():
    return render_template("home.html", user=current_user)


# blog page route
@views.route("/blog")
# user must be logged in to post
@login_required
# home route function
# returns home.html
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_created.desc()).paginate(page=page, per_page=4)
    return render_template("blog.html", user=current_user, posts=posts, endpoint='views.blog')



# user permissions page route
@views.route("/permissions")
# must be logged in to access the page
@login_required
# permissions route function
# returns permissions.html
def permissions():
    if current_user.role != "Guidance Counsellor":
        flash("Access Denied", category='error')
        return redirect(url_for('views.home'))

    users = User.query.all()
    # custom role order
    role_order = {"Guidance Counsellor": 1, "Teacher": 2, "Student": 3}

    # sort by role, then surname, then first name
    users.sort(key=lambda u: (role_order.get(u.role, 99), u.lname.lower(), u.fname.lower()))

    # user counts for dashboard statistics
    counsellor_count = sum(1 for user in users if user.role == "Guidance Counsellor")
    teacher_count = sum(1 for user in users if user.role == "Teacher")
    student_count = sum(1 for user in users if user.role == "Student")

    return render_template("permissions.html", user=current_user, users=users, counsellor_count=counsellor_count, teacher_count=teacher_count, student_count=student_count)



# update user permissions route
@views.route("/update-user/<id>", methods=['GET', 'POST'])
# user must be logged into an admin (guidance counsellor) account to edt user permissions
@login_required
def update_user(id):
    if current_user.role != "Guidance Counsellor":
        flash("Access Denied", category='error')
        return redirect(url_for('views.home'))
        
    user = User.query.filter_by(id=id).first()
    form = UserPermissionUpdateForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.commit()
        flash("User permissions updated!", category="success")
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_created.desc()).paginate(page=page, per_page=4)
        return redirect(url_for('views.permissions'))
        
    elif request.method =='GET':
        form.role.data = user.role
        
    return render_template("update_permissions.html", form=form, user=current_user, posts=user)



# delete user route
@views.route("/delete-user/<id>")
# must be logged in to access the page
@login_required
def delete_user(id):
    if current_user.role != "Guidance Counsellor":
        flash("Access Denied", category='error')
        return redirect(url_for('views.home'))
        
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    flash('User Removed!', category='success')
    return redirect(url_for('views.permissions'))



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
            flash('Post cannot be empty', category='error')
        else:
            post = Post(title=title, content=content, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.blog'))

    return render_template("create_post.html", user=current_user)



# delete blog post route
@views.route("/delete-post/<id>")
# user must be logged in to delete post
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    if not post:
        flash('Post does not exist', category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted!', category='success')
    return redirect(url_for('views.blog'))



# update blog post route
@views.route("/update-post/<id>", methods=['GET', 'POST'])
# user must be logged in to update post
@login_required
def update_post(id):
    post = Post.query.filter_by(id=id).first()
    if post.author != current_user.id:
        flash('You cannot edit this post!', category='error')
        return redirect(url_for("views.blog"))
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated', category='success')
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_created.desc()).paginate(page=page, per_page=4)
        return render_template("blog.html", user=current_user, posts=posts, endpoint="views.blog")
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template("update_post.html", form=form, user=current_user)



#view user posts route
@views.route("/posts/<username>")
@login_required
def posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('No user with that username exists', category='error')
        return redirect(url_for('views.blog'))
    posts = Post.query.filter_by(user=user).order_by(Post.date_created.desc()).paginate(page=page, per_page=4)
    return render_template("posts.html", user=current_user, posts=posts, username=username, endpoint='views.posts')



# blog comment route
@views.route("/create-comment/<post_id>", methods=['POST'])
# user must be logged in to create comment
@login_required
def create_comment(post_id):
    text = request.form.get('text')
    if not text:
        flash('Comment cannot be empty', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added!', category='success')
        else:
            flash('Post does not exist', category='error')

    return redirect(url_for('views.blog'))



# delete comment route
@views.route("/delete-comment/<comment_id>")
# user must be logged in to delete comment
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        flash('Comment does not exist', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted!', category='success')
    return redirect(url_for('views.blog'))



# like comment route
@views.route("/like-post/<post_id>", methods=['POST'])
# user must be logged in to like post
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()
    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})



# book an appointment route
@views.route("/book-appointment", methods=["GET", "POST"])
# user must be logged in to book an appointment
@login_required
def book_appointment():
    if request.method == "POST":
        counsellor_id = request.form.get("counsellor_id")
        reason = request.form.get("reason")
        preferred_date = request.form.get("preferred_date")
        preferred_time = request.form.get("preferred_time")
        notes = request.form.get("notes")

        # "any counsellor" logic
        if counsellor_id == "any":
            counsellor_id = None
        appointment = Appointment(student_id=current_user.id, counsellor_id=counsellor_id, reason=reason, 
                                  preferred_date=preferred_date, preferred_time=preferred_time, notes=notes)

        db.session.add(appointment)
        db.session.commit()
        flash("Appointment Request Submitted!", category="success")
        return redirect(url_for("views.home"))

    counsellors = User.query.filter_by(role="Guidance Counsellor").all()
    return render_template("book_appointment.html", user=current_user, counsellors=counsellors)



# notification centre route
@views.route("/notifications")
# user must be logged in to view and change bookings
@login_required
def notifications():
    if current_user.role != "Guidance Counsellor":
        flash("Access Denied", category="error")
        return redirect(url_for("views.home"))

    appointments = Appointment.query.filter((Appointment.counsellor_id == current_user.id) | (Appointment.counsellor_id == None)
                                            ).order_by(Appointment.date_created.desc()).all()

    return render_template("notifications.html", user=current_user, appointments=appointments)



# claim appointment route
@views.route("/claim-appointment/<int:id>", methods=["POST"])
# user must be logged in to claim appointment
@login_required
def claim_appointment(id):
    if current_user.role != "Guidance Counsellor":
        flash("Access Denied", category="error")
        return redirect(url_for("views.home"))

    appointment = Appointment.query.get(id)

    if not appointment:
        flash("Appointment not found", category="error")
        return redirect(url_for("views.notifications"))

    # only unclaimed appointments can be claimed
    if appointment.counsellor_id is None:
        appointment.counsellor_id = current_user.id
        db.session.commit()
        flash("Appointment claimed!", category="success")

    return redirect(url_for("views.notifications"))



# update booking status route
@views.route("/update-appointment-status/<int:id>", methods=["POST"])
# user must be logged in to update booking status'
@login_required
def update_appointment_status(id):
    if current_user.role != "Guidance Counsellor":
        flash("Access Denied", category="error")
        return redirect(url_for("views.home"))

    appointment = Appointment.query.get(id)

    if not appointment:
        flash("Appointment not found", category="error")
        return redirect(url_for("views.notifications"))

    appointment.status = request.form.get("status")

    db.session.commit()
    flash("Status updated!", category="success")
    return redirect(url_for("views.notifications"))



# contact route
@views.route("/contact")
# contact route function
# returns contact.html
def contact():
    return render_template("contact.html", user=current_user)