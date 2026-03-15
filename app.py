from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SECRET_KEY"] = "your-secret-key-123"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.relationship('Tag', secondary=post_tags, backref='posts')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html")

@app.route("/blog")
def blog():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("blog.html", posts=posts)

@app.route("/blog/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post_detail.html", post=post)

@app.route("/blog/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        post = Post(title=request.form["title"], content=request.form["content"])
        tag_names = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("blog"))
    return render_template("new_post.html")

@app.route("/blog/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        post.tags.clear()
        tag_names = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            post.tags.append(tag)
        db.session.commit()
        return redirect(url_for("post_detail", post_id=post.id))
    return render_template("edit_post.html", post=post)

@app.route("/blog/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("blog"))

@app.route("/tag/<string:tag_name>")
def tag_posts(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    return render_template("tag_posts.html", tag=tag, posts=tag.posts)

@app.route("/search")
def search():
    query = request.args.get("q", "")
    posts = Post.query.filter(
        Post.title.contains(query) | Post.content.contains(query)
    ).order_by(Post.created_at.desc()).all()
    return render_template("search.html", posts=posts, query=query)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("blog"))
        flash("帳號或密碼錯誤")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("blog"))

if __name__ == "__main__":
    app.run(debug=True)