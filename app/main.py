from flask import Flask, render_template, session, request, url_for, redirect, flash, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
import secrets
import hashlib
from PIL import Image
from flask_socketio import SocketIO, emit, send, join_room
from flask_sslify import SSLify
import json
from collections import deque

app = Flask(__name__)
if 'DYNO' in os.environ:
    SSLify(app)

# Secret KEY is different in production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins='*')
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get("EMAIL_BLOGGY")
app.config['MAIL_PASSWORD'] = os.environ.get("PASSWORD_BLOGGY")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def make_session_permanent():
    session.permanent = True


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String())
    profile_pic = db.Column(
        db.String(40), nullable=False, default='default.jpg')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    commenter = db.relationship('Comment', backref='commenter', lazy='dynamic')
    access_token = db.Column(db.String(180))
    liker = db.relationship('Like', backref='liker', lazy='dynamic')
    followed = db.relationship(
        'Follower', backref='followed', foreign_keys='Follower.followed_id', lazy='dynamic')
    follower = db.relationship(
        'Follower', backref='follower', foreign_keys='Follower.follower_id', lazy='dynamic')
    sender = db.relationship('Message', backref='sender',
                             foreign_keys='Message.sender_id', lazy='dynamic')
    receiver = db.relationship('Message', backref='receiver',
                               foreign_keys='Message.receiver_id', lazy='dynamic')
    bio_content = db.Column(db.String(1000))
    verified = db.Column(db.Boolean(), default=False)

    def has_liked_post(self, post):
        return Like.query.filter(
            Like.liker_id == self.id,
            Like.liked_id == post.id).count() > 0

    def has_followed_user(self, user):
        return Follower.query.filter(
            Follower.follower_id == self.id,
            Follower.followed_id == user.id).count() > 0

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(100), nullable=False)
    post_content = db.Column(db.String(1000), nullable=False)
    post_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commented = db.relationship('Comment', backref='commented', lazy='dynamic')
    likes = db.relationship('Like', backref='liked', lazy='dynamic')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commented_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_body = db.Column(db.String(100))


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    liked_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    liker_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(), nullable=False)
    message = db.Column(db.String(), nullable=False)
    time = db.Column(db.String(), nullable=False)
    message_time = db.Column(
        db.DateTime(), nullable=False, default=datetime.utcnow)
    read = db.Column(db.Boolean())
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Administration


class AdminModelView(ModelView):
    def is_accessible(self):
        if 'logged_in' in session:
            return True
        else:
            abort(403)


admin = Admin(app, name='Bloggy Admin', template_mode='bootstrap3')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Post, db.session))
admin.add_view(AdminModelView(Comment, db.session))
admin.add_view(AdminModelView(Like, db.session))
admin.add_view(AdminModelView(Follower, db.session))
admin.add_view(AdminModelView(Message, db.session))


class PostForm(FlaskForm):
    post_title = StringField(validators=[InputRequired(), Length(
        min=4, max=40)], render_kw={"placeholder": "Title"})
    post_content = TextAreaField(validators=[InputRequired(), Length(
        min=4, max=1000)], render_kw={"placeholder": "Description"})
    submit = SubmitField("Upload Post")


class UpdatePostForm(FlaskForm):
    post_title = StringField("Title", validators=[
        InputRequired(), Length(min=4, max=40)])
    post_content = TextAreaField("Description", validators=[
        InputRequired(), Length(min=4, max=1000)])
    submit = SubmitField("Update Post")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(
        min=4, max=50)], render_kw={"placeholder": "Username"})
    password = PasswordField("Password", validators=[InputRequired(), Length(
        min=4)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

    def validate_username(self, username):
        username = User.query.filter_by(username=username.data).first()
        if not username:
            raise ValidationError('Account does not exist.')


class BioForm(FlaskForm):
    bio = TextAreaField('Bio', [Length(min=0, max=1000)])
    submit = SubmitField("Update Bio")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(
        message="Invalid Email"), Length(max=50)], render_kw={"placeholder": "Email Address"})
    username = StringField("Username", validators=[InputRequired(), Length(
        min=4, max=15)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=4)], render_kw={"placeholder": "Password (4 minimum)"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one.")

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                "That email address belongs to different user. Please choose a different one.")


class UpdateAccount(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(
        message="Invalid Email"), Length(max=50)], render_kw={"placeholder": "Edit Email"})
    username = StringField("Username", validators=[InputRequired(), Length(
        min=4, max=15)], render_kw={"placeholder": "Edit Username"})
    bio = TextAreaField([Length(min=0, max=1000)], render_kw={
        "placeholder": "Edit Bio"})
    profile_pic = FileField(validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Account')

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username already exists. Please choose a different one.")

    def validate_email(self, email):
        if current_user.email != email.data:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError(
                    "That email address belongs to different user. Please choose a different one.")


class ForgotPasswordForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(
        message="Invalid Email"), Length(max=50)], render_kw={"placeholder": "Email"})
    submit = SubmitField("Send Reset Email")


class ResetPasswordForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(
        message="Invalid Email"), Length(max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=4)], render_kw={"placeholder": "Password (4 minimum)"})


class ChangePasswordForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(
        message="Invalid Email"), Length(max=50)], render_kw={"placeholder": "Email"})
    current_password = PasswordField(validators=[InputRequired(), Length(
        min=4)], render_kw={"placeholder": "Current Password"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=4)], render_kw={"placeholder": "New Password (4 minimum)"})
    submit = SubmitField("Change Password")


class DeleteAccountForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(
        message="Invalid Email"), Length(max=50)], render_kw={"placeholder": "Email"})
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=15)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Delete My Account")


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[InputRequired(), Length(
        min=4)], render_kw={"placeholder": "Enter Comment"})
    submit = SubmitField("Add Comment")


class UserSearchForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=15)], render_kw={"placeholder": "Search For Users"})


class MessageForm(FlaskForm):
    message = StringField(validators=[InputRequired(), Length(
        min=4, max=200)], render_kw={"placeholder": "Send A Message"})


# Error handling


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404 Page Not Found</h1>", 404


@app.errorhandler(403)
def page_not_found(e):
    return "<h1>403 You do not have permission to do that.</h1>", 403


# Landing Page
@app.route('/')
@app.route('/home')
def home():

    if current_user.is_authenticated:
        return redirect('dashboard')
    else:
        return render_template('home.html', title='Home')


# Login Page
@app.route("/login", methods=['GET', 'POST'])
def login():
    loginform = LoginForm()
    registerform = RegisterForm()
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, loginform.password.data):
                login_user(user)
                return redirect(url_for("dashboard"))

    if registerform.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            registerform.password.data).decode('utf-8')
        new_user = User(username=registerform.username.data,
                        email=registerform.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Your account has successfully been created!")
        return redirect(url_for('login'))

    if current_user.is_authenticated:
        return redirect('dashboard')
    else:
        return render_template('login.html', title='Login', loginform=loginform, registerform=registerform)


# User Home Page
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserSearchForm()
    email_w_key = current_user.email+app.config['SECRET_KEY']
    email_encoding = email_w_key.encode('utf-8')
    hashed_token = hashlib.sha512(email_encoding).hexdigest()
    current_user.access_token = hashed_token
    db.session.commit()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash("User has been found!")
            return redirect(url_for('user', username=form.username.data))
        else:
            flash("User does not exist.")

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(
        Post.post_date.desc()).paginate(page=page, per_page=4)
    following = Follower.query.filter_by(follower=current_user).all()
    total_posts = Post.query.all()

    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')

    return render_template("dashboard.html", posts=posts, title="My Dashboard", total_posts=len(total_posts), form=form)


# Save picture into directory
def save_picture(form_profile_pic):
    rand_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_profile_pic.filename)
    picture_name = rand_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_name)
    form_profile_pic.save(picture_path)

    output_size = (125, 125)
    i = Image.open(form_profile_pic)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_name


# User Account Information
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    posts = Post.query.filter_by(author=current_user).all()
    post_total = 0
    for i in posts:
        post_total += 1
    form = UpdateAccount()
    if form.validate_on_submit():
        if form.profile_pic.data:
            picture_file = save_picture(form.profile_pic.data)
            current_user.profile_pic = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio_content = form.bio.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio_content
    profile_pic = url_for(
        'static', filename='profile_pics/' + current_user.profile_pic)
    return render_template("account.html", name=current_user.username, email=current_user.email, title="My Profile", form=form, posts=post_total, profile_pic=profile_pic)


# If a user visits another user's profile
@app.route("/user/<username>")
@login_required
def user(username):
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user).paginate(page=page, per_page=3)
    followers = Follower.query.filter_by(followed=user).all()
    followers_total = 0
    for follower in followers:
        followers_total += 1

    return render_template('user.html', title=user.username, user=user, posts=posts, followers_total=followers_total, followers=followers)


# Change Password
@app.route("/changepassword", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        hashed_password = bcrypt.generate_password_hash(
            form.new_password.data).decode('utf-8')
        if form.email.data != current_user.email:
            flash("Invalid email")
        if not bcrypt.check_password_hash(current_user.password, form.current_password.data):
            flash("Invalid password")
        else:
            current_user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated!')
            return redirect(url_for('account'))
    return render_template("changepw.html", form=form, title="Change Password")


# Create the post
@app.route("/post", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    if form.validate_on_submit():
        post = Post(post_title=form.post_title.data,
                    post_content=form.post_content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!")
        return redirect(url_for('dashboard'))
    return render_template("create_post.html", form=form, title="New Post", legend='New Post')


# Post Id
@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')

    # Get post
    post = Post.query.get_or_404(post_id)
    return render_template('postid.html', title=post.post_title, post=post)


# Update Posts
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    form = PostForm()
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if form.validate_on_submit():
        post.post_title = form.post_title.data
        post.post_content = form.post_content.data
        db.session.commit()
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.post_title.data = post.post_title
        form.post_content.data = post.post_content
    flash("Your post has been updated!", "success")
    return render_template('update_post.html', title='Update Post', form=form, post=post_id)


# Delete the post
@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    form = PostForm()
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(commented=post).all()
    likes = Like.query.filter_by(liked=post).all()
    if current_user != post.author:
        abort(403)
    for comment in comments:
        db.session.delete(comment)
        db.session.commit()
    for like in likes:
        db.session.delete(like)
        db.session.commit()
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('dashboard'))


# Comment on post
@app.route('/post/<int:post_id>/comment', methods=['GET', 'POST'])
@login_required
def comment_on_post(post_id):
    form = CommentForm()
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        comment = Comment(commented=post, commenter=current_user,
                          comment_body=form.comment.data)
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been posted.", 'success')
        return redirect(url_for('view_comments', post_id=post_id))
    return render_template('comment.html', form=form)


# Delete a comment
@app.route('/post/<int:post_id>/<int:comment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_comment(post_id, comment_id):
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted.', 'success')
    return redirect(url_for('view_comments', post_id=post_id))


# View Comments
@app.route('/post/<int:post_id>/comments', methods=['GET', 'POST'])
@login_required
def view_comments(post_id):
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(commented_id=post_id).all()
    return render_template('view_comments.html', comments=comments, post=post, title=f'Comments of {post.post_title}', total=len(comments))


@app.route('/post/<int:post_id>/<action>', methods=['GET', 'POST'])
@login_required
def like_post(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    if action == 'like' and current_user.has_liked_post(post):
        flash('Already liked post')
        return redirect(request.referrer)
    if action == 'like':
        new_like = Like(liker=current_user, liked=post)
        db.session.add(new_like)
        db.session.commit()

    if action == 'unlike':
        like = Like.query.filter_by(liker=current_user, liked=post).delete()
        db.session.commit()

    return redirect(request.referrer)


@app.route('/post/<int:post_id>/view-likes', methods=['GET', 'POST'])
@login_required
def view_likes(post_id):
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    post = Post.query.filter_by(id=post_id).first_or_404()
    likes = Like.query.filter_by(liked_id=post_id).all()
    return render_template('likers.html', likes=likes, post=post, title=f'Likes of {post.post_title}')


@app.route('/<action>/user/<username>', methods=['GET', 'POST'])
@login_required
def follow_action(action, username):
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    user = User.query.filter_by(username=username).first()

    ''' user variable is a user object. The username paramter in the url
    is used to query from the database to check if the user exists or not.
    In the new_follower variable, the followed=user in the Follower() object
    means that the actual followed person is the user object.
    '''

    if action == 'follow' and current_user.has_followed_user(user):
        flash('Already following this user.', 'info')
        return redirect(url_for('user', username=username))

    if action == 'follow':
        if user.username == current_user.username:
            flash('You cannot follow yourself!', 'info')
            return redirect(url_for('user', username=username))
        new_follower = Follower(followed=user, follower=current_user)
        db.session.add(new_follower)
        db.session.commit()
        flash(f'Started following {username}', 'success')
        return redirect(url_for('user', username=username))

    if action == 'unfollow':
        follower = Follower.query.filter_by(
            followed=user, follower=current_user).delete()
        db.session.commit()
        flash(f'Unfollowed {username}', 'info')
        return redirect(url_for('user', username=username))


@app.route('/user/<username>/view-followers', methods=['GET', 'POST'])
@login_required
def view_followers(username):
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    user = User.query.filter_by(username=username).first()
    followers = Follower.query.filter_by(followed=user).all()
    return render_template('followers.html', user=user, followers=followers, title=f'Followers of {user.username}')


@app.route('/user/<username>/following', methods=['GET', 'POST'])
@login_required
def view_following(username):
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    user = User.query.filter_by(username=username).first()
    following = Follower.query.filter_by(follower=user).all()
    return render_template('following.html', user=user, following=following, title=f'{user.username} is following')


# Delete User Account
@app.route("/delete_account", methods=['GET', 'POST'])
@login_required
def delete_account():
    if current_user.username == 'admin' and current_user.email == 'arpanneupane19@gmail.com':
        session['logged_in'] = True
        return redirect('/admin')
    form = DeleteAccountForm()
    posts = Post.query.filter_by(author=current_user).all()
    sent_messages = Message.query.filter_by(sender=current_user).all()
    received_messages = Message.query.filter_by(receiver=current_user).all()
    comments = Comment.query.filter_by(commenter=current_user).all()
    likes = Like.query.filter_by(liker=current_user).all()
    follows = Follower.query.filter_by(follower=current_user).all()
    user = User.query.filter_by(email=form.email.data).first()
    if form.validate_on_submit():
        if form.email.data != current_user.email or form.username.data != current_user.username:
            flash(
                'The email or username you provided are not associated with your account.')
            return redirect(url_for('delete_account'))
        for post in posts:
            db.session.delete(post)
        for message in sent_messages:
            db.session.delete(message)
        for message in received_messages:
            db.session.delete(message)
        for comment in comments:
            db.session.delete(comment)
        for like in likes:
            db.session.delete(like)
        for follow in follows:
            db.session.delete(follow)

        db.session.delete(user)
        db.session.commit()
        flash('Your account has been deleted', 'success')
        return redirect(url_for('home'))
    return render_template("deleteacc.html", form=form, title="Delete My Account")


@app.route("/inbox", methods=['GET', 'POST'])
@login_required
def inbox():
    received_messages = Message.query.filter_by(receiver=current_user).all()
    sent_messages = Message.query.filter_by(sender=current_user).all()

    inbox_list = []

    for message in received_messages:
        sender = message.sender
        if sender in inbox_list:
            inbox_list.insert(0, inbox_list.pop(inbox_list.index(sender)))
        if sender not in inbox_list:
            inbox_list.insert(0, sender)

    for message in sent_messages:
        receiver = message.receiver
        if receiver in inbox_list:
            inbox_list.insert(0, inbox_list.pop(inbox_list.index(receiver)))
        if receiver not in inbox_list:
            inbox_list.insert(0, receiver)

    return render_template("inbox.html", title="Inbox", inbox_list=inbox_list, length=len(inbox_list))


# Map room to a list of users
room_to_users = dict({})

# Map username to a room
user_to_room = dict({})


@socketio.on('connectUser')
def connect_user(data):
    # This is event is for joining the user into the room when they're trying to chat.
    room = data['room']
    username = data['username']
    global room_to_users
    global user_to_room

    if room in room_to_users.keys():
        if username in room_to_users[room]:
            print('exists')
        else:
            room_to_users[room].append(username)
    if not room in room_to_users.keys():
        room_to_users[room] = [username]
    join_room(room)
    user_to_room[username] = room
    print(f'room to users: {room_to_users}')
    print(f'user to room: {user_to_room}')

    # IF there were previous messages, then it will query them by the room & receiver and set the read status to True
    messages = Message.query.filter_by(room=room, receiver=current_user).all()

    for i in room_to_users[room]:
        for message in messages:
            message.read = True
            db.session.commit()


@socketio.on('disconnect')
def disconnect_user():
    username = current_user.username
    room = user_to_room.get(username)

    # This is to remove the user(s) from the dictionary.
    '''
    I first check if they exist in the room or not,
    if they do, I will iterate through the array of users in the room,
    then for each index, if the value of the index is rqual to the current user's
    username, then it will remove that user from the user_to_room dict. 
    This will remove the user's name from the array as well as remove their name 
    from the user_to_room dict.
    '''

    '''
    After all of those checks, the app will check the length of the array to see 
    how many people are in the room, if there are 0 people in the room, it will delete the room code
    from the room_to_users dictionary.
    '''
    if username in room_to_users[room]:
        for i in room_to_users[room]:
            if i == username:
                room_to_users[room].remove(i)
                user_to_room.pop(username)
                print(f'user to room: {user_to_room}')
        if len(room_to_users[room]) == 0:
            room_to_users.pop(room)
        print(f'room to users: {room_to_users}')
    print(f"{username} has disconnected from room {room}")


@socketio.on('chat')
def chat(msg):
    # This is emitted when a user sends a message, the handling is done here
    print(msg)

    # Get the sender and receiver of the message from object
    message_sender = msg['sender']
    message_receiver = msg['receiver']

    # Get the room for which the message is being sent to
    room = msg['room']

    # Time of the message
    time = msg['time']

    read = False

    # Query the sender and receiver to see if they exist
    receiver = User.query.filter_by(username=message_receiver).first()
    sender = User.query.filter_by(username=message_sender).first()

    # Create new message object for adding message to db
    if (len(room_to_users[room])) == 1:
        new_message = Message(
            room=room, read=False, time=time, message=msg['message'], sender=sender, receiver=receiver)
        db.session.add(new_message)
        db.session.commit()

    if (len(room_to_users[room])) == 2:
        new_message = Message(
            room=room, read=True, time=time, message=msg['message'], sender=sender, receiver=receiver)
        db.session.add(new_message)
        db.session.commit()
    # send message to the people in the room.
    send(msg, room=room)


@app.route('/message/<user>', methods=['GET', 'POST'])
@login_required
def messaging(user):

    # Query receiver
    user = User.query.filter_by(username=user).first_or_404()

    '''
        In the message event the room code is like this: <user1>,<user2>
        The room code is generated from the frontend and when converting array to string in JavaScript,
        there's a comma in between the elements.
        In Python, there was no comma, thus I had to insert one when joining the elements of the list.
        When they're joined, the new value is stored in the room_code variable which is used to query the db.
    '''
    room = [user.username, current_user.username]
    room.sort()
    room_code = ','.join(room)

    # Query messages from db by room
    messages = Message.query.filter_by(room=room_code).all()

    num_of_messages = len(messages)

    # Validation
    if current_user.username == user.username:
        flash("You can't message yourself.")
        return redirect(url_for('user', username=user.username))
    return render_template('message.html', title='Messaging', receiver=user, messages=messages, num_of_messages=num_of_messages)


@app.route('/use-the-bloggy-api')
def use_api():
    token = current_user.access_token
    return render_template('use_api.html', title='Use The API', token=token)


# Bloggy API
@app.route('/api/<token>')
def api(token):
    user = User.query.filter_by(access_token=token).first_or_404()
    posts = Post.query.filter_by(author=user).all()

    followers = Follower.query.filter_by(followed=user).all()
    followed = Follower.query.filter_by(follower=user).all()

    follower_total = 0
    for follower in followers:
        follower_total += 1

    following_total = 0
    for follow in followed:
        following_total += 1

    post_total = 0
    for post in posts:
        post_total += 1

    if user is None:
        return "404"

    return {
        'total_posts': post_total,
        'followers': follower_total,
        'following': following_total,
        'username': f'{user.username}',
        'user_id': f'{user.id}'
    }


# Logout
@app.route("/logout")
@login_required
def logout():
    session.clear()
    logout_user()
    flash("You have been logged out.", 'info')
    return redirect(url_for("login"))

# Reset email


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Forgot your password?',
                  sender='bloggywebsite@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_password', token=token, _external=True)}
If you did not make this request then simply ignore this email.
'''
    mail.send(msg)


# Forgot password
@app.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent to reset your password.", 'success')

    return render_template("forgotpw.html", form=form, title="Forgot Password")


# Reset password
@app.route("/resetpassword/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('home'))
    return render_template('resetpw.html', title='Reset Password', form=form)
