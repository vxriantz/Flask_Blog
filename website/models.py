from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin



# database model for user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    fname = db.Column(db.String(20))
    lname = db.Column(db.String(20))
    username = db.Column(db.String(150), unique=True)
    role = db.Column(db.String(150))
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="user", cascade="all, delete-orphan")
    likes = db.relationship("Like", backref="user", cascade="all, delete-orphan")
    # appointments assigned to this guidance counsellor
    appointments = db.relationship('Appointment', foreign_keys="Appointment.counsellor_id", back_populates="counsellor")



# database model for blog post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='post', cascade="all, delete-orphan")



# database model for blog comment
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), unique=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)



# database model for blog likes
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)



# database model for appointment bookings
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    counsellor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) 
    reason = db.Column(db.String(200))
    urgency = db.Column(db.String(50))
    preferred_day = db.Column(db.String(20))
    preferred_period = db.Column(db.String(20))
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default="Pending")
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    # relationship linking appointment to the student who created it
    student = db.relationship('User', foreign_keys=[student_id])
    # relationship linking appointment to the assigned guidance counsellor
    counsellor = db.relationship('User', foreign_keys=[counsellor_id], back_populates="appointments")