from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1z2x3c4v5b6n7m'


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



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if username != user:
            username_error = "Uh oh, looks like you don't have an account yet, click 'signup' to create one!"
            return render_template('login.html', username=username, username_error=username_error)
        elif username == user and password != user.password:
            password_error = "Yikes, that's the wrong password."
            return render_template('login.html', username=username, password_error=password_error)
        elif username == user and password == user.password:
            return render_template('newpost.html')


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
            print(len(username))
        if ' ' in password or len(password) < 3:
            password_error = "Your password should be at least 3 characters longs and not contain spaces."
        if password != verify:
            verify_error = "Please make sure your passwords match!"
        print(len(username))
        return render_template('signup.html', username=username, empty_error=empty_error, username_error=username_error, password_error=password_error, verify_error=verify_error)
        if not empty_error and not username_error and not password_error and not verify_error: 
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')


@app.route('/blog', methods=['POST', 'GET'])
def index():
    posts = Blog.query.all()
    args = request.args.get('id')
    blog = Blog.query.filter_by(id=args).first()

    if not args:
        return render_template('blog.html',title="Build a Blog", 
        posts=posts)
    else:
        return render_template('/blogpost.html', blog=blog)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        new_post = Blog(post_title, post_body)
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

        return redirect('/blog?id='+ str(blog_id))
    
    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()