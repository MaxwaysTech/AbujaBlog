from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField


class CreatePost(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[DataRequired()])
    img_url = StringField(label="Img_url", validators=[DataRequired()])
    img_url1 = StringField(label="Img_url1", validators=[DataRequired()])
    img_url2 = StringField(label="Img_url2", validators=[DataRequired()])
    img_url3 = StringField(label="Img_url3", validators=[DataRequired()])
    img_url4 = StringField(label="Img_url4", validators=[DataRequired()])
    img_url5 = StringField(label="Img_url5", validators=[DataRequired()])
    img_url6 = StringField(label="Img_url6", validators=[DataRequired()])
    location = StringField(label="Location", validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField(label="Add Post")


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    password = StringField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Sign In")


class RegisterForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired()])
    username = StringField(label="Username", validators=[DataRequired()])
    password = StringField(label="Password", validators=[DataRequired()])
    submit = SubmitField(label="Sign Up")


class CommentForm(FlaskForm):
    text = CKEditorField("Add your comment")
    submit = SubmitField("Submit comment")
