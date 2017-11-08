from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.navigation import Navigation
from hashutils import make_pw_hash, check_pw_hash

#create and configure the Flask app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1z2x3c4v5b6n7m'
app.static_folder = 'static'
nav = Navigation(app)
title= 'Blogz'

#define database types
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

#function to return text file as string for css workaround (add css via <style> tags to base.html template)
def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

#Set up Jinja2 navbar elements to iterate in bootstrap navbar in base.html template
nav.Bar('left', [
    nav.Item('Home', 'index'),
    nav.Item('All Posts', 'list_blogs'),
    nav.Item('New Post', 'newpost')
])

nav.Bar('right', [
    nav.Item('Login', 'login'),
    nav.Item('Logout', 'logout')
])

#prevent users from going to newpost page without being logged in
@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

#home/index page lists all blog users as links
@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users, title=title)

#login checks login credentials against user database
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            username_error = "Uh oh, looks like you don't have an account yet, click 'signup' to create one!"
            return render_template('login.html', username=username, username_error=username_error)
        elif user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            print(session['username'])
            return redirect('/newpost')
        else:
            password_error = "Yikes, that's the wrong password."
            return render_template('login.html', username=username, password_error=password_error)

#take input to create new users in database
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        empty_error = ''
        username_error = ''
        password_error = ''
        verify_error = ''
        check_user = User.query.filter_by(username=username).first()

#input verification
        if not username or not password:
            empty_error = "Forget something? Make sure you fill out each field, please."
        if check_user:
            username_error = "That user already exists!"
        if ' ' in username or len(username) < 3:
            username_error = "Please enter a username that is at least 3 characters longs and doesn't contain spaces."
            username = ''
        if ' ' in password or len(password) < 4:
            password_error = "Your password should be at least 3 characters longs and not contain spaces."
        if password != verify:
            verify_error = "Please make sure your passwords match!"

#if pass verification, update database     
        if not empty_error and not username_error and not password_error and not verify_error: 
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', username=username, empty_error=empty_error, username_error=username_error, password_error=password_error, verify_error=verify_error)

#delete user from session on logout
@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

#all blog rendering done here
@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    posts = Blog.query.all()
    blog_args = request.args.get('id')
    user_args = request.args.get('user')
    user = User.query.filter_by(username=user_args).first()
    user_posts = Blog.query.filter_by(owner=user).all()
    blog = Blog.query.filter_by(id=blog_args).first()

#if no user is selected, show all blogs posts
    if not blog_args and not user_args:
        return render_template('blog.html',title="Build a Blog", 
        posts=posts)
#if a blog is selected, only show it      
    elif blog_args:
        return render_template('/blogpost.html', blog=blog, user=user, user_posts=user_posts)
#if a user is selected, show all of their posts   
    elif user_args:
        return render_template('/userposts.html', blog=blog, user=user, user_posts=user_posts)

#update Blog database with new blog post input
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        post_owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(post_title, post_body, post_owner)
        db.session.add(new_post)
        db.session.commit()
        blog = Blog.query.filter_by(id=new_post.id).first()
        blog_id = blog.id
        title_error = request.args.get('title_error')
        body_error = request.args.get('title_error')

#input verification
        if not post_title:
            title_error = "Please enter a title."
            post_title = ''
        if not post_body:
            body_error = "Please enter a body."
            post_body = ''
        if title_error or body_error:
            return render_template('newpost.html', post_title=post_title, post_body=post_body, title_error=title_error, body_error=body_error)
        print(blog_id)
        return redirect('/blog?id='+ str(blog_id))
    
    else:
        return render_template('newpost.html')



if __name__ == '__main__':
    app.run()