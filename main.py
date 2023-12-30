from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from form import RegisterForm, LoginForm
from form import CreatePost, CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
db.init_app(app)

Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def admin_only(func):
    @login_required
    @wraps(func)
    def decorator_wrapper(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return func(*args, **kwargs)

    return decorator_wrapper


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    username = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    children = relationship("Comment", back_populates="parent")


class BlogPost(db.Model):
    __tablename__ = "blog_post"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    author = relationship("User", back_populates="posts")
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    img_url1 = db.Column(db.String(250), nullable=False)
    img_url2 = db.Column(db.String(250), nullable=False)
    img_url3 = db.Column(db.String(250), nullable=False)
    img_url4 = db.Column(db.String(250), nullable=False)
    img_url5 = db.Column(db.String(250), nullable=False)
    img_url6 = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="blog_post")


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.Text(100))
    post_id = db.Column(db.Integer, db.ForeignKey("blog_post.id"))
    parent = relationship("User", back_populates="children")
    blog_post = relationship("BlogPost", back_populates="comments")


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    result = db.session.execute(db.select(User).where(User.email == form.email.data))
    user = result.scalar()
    if form.validate_on_submit():
        if user:
            flash(message="You've already signed up with this email, log in instead")
            return redirect(url_for('login'))
        else:
            password_to_hash = generate_password_hash(password=form.password.data, method="pbkdf2:sha256",
                                                      salt_length=8)
            add_user = User(
                email=form.email.data,
                username=form.username.data,
                password=password_to_hash
            )
            db.session.add(add_user)
            db.session.commit()
            login_user(add_user)
            return render_template("success.html", name=current_user.username)
    return render_template('register.html', form=form, name=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if not user:
            flash("Email doesn't exist, please try again!")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Password doesn't exist, please try again!")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template('login.html', form=form, current_user=current_user)


@app.route('/post/<int:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            add_comment = Comment(
                text=form.text.data,
                parent=current_user,
                blog_post=requested_post
            )
            db.session.add(add_comment)
            db.session.commit()
            return redirect(url_for('show_post', post_id=requested_post.id))
        else:
            flash(message="You need to login/register to comment on the post")
            return redirect(url_for('login'))
    return render_template("post.html", form=form, post=requested_post, current_user=current_user)


@app.route("/add-post", methods=["GET", "POST"])
@admin_only
def create_post():
    form = CreatePost()
    if form.validate_on_submit():
        add_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author=current_user,
            body=form.body.data,
            img_url=form.img_url.data,
            img_url1=form.img_url1.data,
            img_url2=form.img_url2.data,
            img_url3=form.img_url3.data,
            img_url4=form.img_url4.data,
            img_url5=form.img_url5.data,
            img_url6=form.img_url6.data,
            location=form.location.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(add_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('new_post.html', form=form)


@app.route('/edit_post/<int:post_id>', methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePost(
        title=post.title,
        subtitle=post.subtitle,
        body=post.body,
        img_url=post.img_url,
        img_url1=post.img_url1,
        img_url2=post.img_url2,
        img_url3=post.img_url3,
        img_url4=post.img_url4,
        img_url5=post.img_url5,
        img_url6=post.img_url6,
        location=post.location
    )

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.body = edit_form.body.data
        post.img_url = edit_form.img_url.data
        post.img_url1 = edit_form.img_url1.data
        post.img_url2 = edit_form.img_url2.data
        post.img_url3 = edit_form.img_url3.data
        post.img_url4 = edit_form.img_url4.data
        post.img_url5 = edit_form.img_url5.data
        post.img_url6 = edit_form.img_url6.data
        post.location = edit_form.location.data
        db.session.commit()
        return redirect(url_for('get_all_posts', post_id=post.id))
    return render_template('new_post.html', form=edit_form, edit_post=True, current_user=current_user)


@app.route('/delete/<int:post_id>')
@admin_only
def delete(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route('/success')
@admin_only
def success():
    return render_template("success.html", name=current_user.username)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
