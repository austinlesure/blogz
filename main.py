from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://__user__:__password__@localhost:3306/sandwichees'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(12000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['GET'])
def index():
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    blogs = Blog.query.all()
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog?id=' + str(new_blog.id))
    else:
        return render_template('newpost.html',title="The Blogz!")

@app.route('/blog', methods=['GET'])
def blog_post():
    if request.args.get('id'):        
        id = request.args.get("id")
        blog = Blog.query.filter(Blog.id == id).first()
        return render_template('blog.html', title = 'The Blogz! - ' + blog.title, blog_title = blog.title, blog_body = blog.body)
    else:
        blogs = Blog.query.all()
        return render_template('main.html', title = 'The Blogz', blogs = blogs)

if __name__ == '__main__':
    app.run()
