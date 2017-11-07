from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.navigation import Navigation

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1z2x3c4v5b6n7m'
app.static_folder = 'static'
nav = Navigation(app)

title= 'Blogz'

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
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

nav.Bar('left', [
    nav.Item('Home', 'index'),
    nav.Item('All Posts', 'list_blogs'),
    nav.Item('New Post', 'newpost')
])

nav.Bar('right', [
    nav.Item('Login', 'login'),
    nav.Item('Logout', 'logout')
])

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'blog', 'list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users, title=title)

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
        elif user and password != user.password:
            password_error = "Yikes, that's the wrong password."
            return render_template('login.html', username=username, password_error=password_error)
        elif user and password == user.password:
            session['username'] = username
            nav.Bar('left', [
                nav.Item('Home', 'index'),
                nav.Item('All Posts', 'blog'),
                nav.Item('New Post', 'newpost')
            ])
            full-nav
            print(session['username'])
            return redirect('/newpost')


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
        
        if not empty_error and not username_error and not password_error and not verify_error: 
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html', username=username, empty_error=empty_error, username_error=username_error, password_error=password_error, verify_error=verify_error)

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    posts = Blog.query.all()
    blog_args = request.args.get('id')
    user_args = request.args.get('user')
    user = User.query.filter_by(username=user_args).first()
    user_posts = Blog.query.filter_by(owner=user).all()
    blog = Blog.query.filter_by(id=blog_args).first()

    if not blog_args and not user_args:
        return render_template('blog.html',title="Build a Blog", 
        posts=posts)
    elif blog_args:
        return render_template('/blogpost.html', blog=blog, user=user, user_posts=user_posts)
    elif user_args:
        return render_template('/userposts.html', blog=blog, user=user, user_posts=user_posts)


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

        if not post_title:
            title_error = "Please enter a title."
            post_title = ''
        if not post_body:
            body_error = "Please enter a body."
            post_body = ''
        if title_error or body_error:
            return render_template('newpost.html', post_title=post_title, post_body=post_body, title_error=title_error, body_error=body_error)
            #return redirect('/newpost?' + 'post_title=' + post_title + '&post_body=' + post_body
                #+ '&title_error=' + title_error + '&body_error=' + body_error)
        print(blog_id)
        return redirect('/blog?id='+ str(blog_id))
    
    else:
        return render_template('newpost.html')



if __name__ == '__main__':
    app.run()