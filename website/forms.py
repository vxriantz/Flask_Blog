from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from .models import User, Post



class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class UserPermissionUpdateForm(FlaskForm):
    role = RadioField("Role", choices=[('Admin'), ('Teacher'), ('Student')],validators=[DataRequired()])
    submit = SubmitField('Update')