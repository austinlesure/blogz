from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://____________@localhost:3306/sandwichees'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'oh_so_secret'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(12000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(32))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog_post', 'single_user']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title = 'Blogz', users = users)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(username = session['user']).first()
    if request.method == 'POST':
        error_msg = ''
        blog_title = request.form['blog_title']        
        blog_body = request.form['blog_body']
        if len(blog_title) == 0:
            error_msg = ' Title Missing! '
        if len(blog_body) == 0:
            error_msg += ' Body Empty! '
        if len(blog_title) == 0 or len(blog_body) == 0:
            return render_template('newpost.html',title="The Blogz!", blog_title = blog_title, blog_body = blog_body, error_msg = error_msg)
        new_blog = Blog(blog_title, blog_body, owner)
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
        user = User.query.filter(User.id == blog.owner_id).first()
        return render_template('blog.html', user_id = user.id, username = user.username, title = 'The Blogz! - ' + blog.title, blog_title = blog.title, blog_body = blog.body)
    else:
        blogs = Blog.query.all()
        return render_template('main.html', title = 'The Blogz', blogs = blogs)

@app.route('/single_user', methods=['GET'])
def single_user():
    if request.args.get('id'):        
        id = request.args.get("id")
        user = User.query.filter(User.id == id).first()
        blogs = []
        blogs += Blog.query.filter(Blog.owner_id == int(id))
        return render_template('single_user.html', title = 'The Blogz! - ' + user.username, h2_title = user.username, blogs = blogs)
    else:
        return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
    error_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not User.query.filter(User.username == username).first():
            error_msg = 'No such user'
            return render_template('login.html', title = 'Login', error_msg = error_msg)
        else:
            user = User.query.filter(User.username == username).first()
        if password != user.password:
            error_msg = 'Password incorrect'
            return render_template('login.html', title = 'Login', user = user.username, error_msg = error_msg)
        else:
            session['user'] = user.username
            return redirect('/')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error_msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_msg = 'Duplicate User'
            return render_template('signup.html', title = 'Sign Up', error_msg = error_msg)
        if len(username) < 3 or len(password) < 3:
            error_msg = 'Username and/or password must be at least 3 characters long'
            return render_template('signup.html', title = 'Sign Up', error_msg = error_msg)
        if password != verify:
            error_msg = 'Passwords do not match'
            return render_template('signup.html', title = 'Sign Up', username = username, error_msg = error_msg)
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['user'] = new_user.username
        return redirect('/')
        
    return render_template('signup.html', title = 'Sign Up')

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/')

if __name__ == '__main__':
    app.run()