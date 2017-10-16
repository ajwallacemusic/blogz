from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body


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