import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    signature = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    message = db.relationship('Message', backref=db.backref('comments', lazy=True))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    g.show_admin_link = current_user.is_authenticated and current_user.is_admin

@app.route('/')
def home():
    return render_template('home.html', title="Revolución Torteña")

@app.route('/news')
def news():
    return render_template('news.html', title="Revolución Torteña - Noticias")

@app.route('/foro')
def foro():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('foro.html', messages=messages, title="Foro")

@app.route('/postear', methods=['GET', 'POST'])
@login_required
def postear():
    if request.method == 'POST':
        title = request.form['title']
        message_text = request.form['message']
        signature = request.form['signature']
        ip_address = request.remote_addr
        user_id = current_user.id
        if not title or not message_text or not signature:
            flash('Todos los campos son obligatorios')
        else:
            message = Message(title=title, message=message_text, signature=signature, ip_address=ip_address, user_id=user_id)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('foro'))
    return render_template('postear.html', title="Postear")

@app.route('/message/<int:message_id>', methods=['GET', 'POST'])
def message_detail(message_id):
    message = Message.query.get_or_404(message_id)
    highlighted_comment_id = None
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need to login to comment.', 'danger')
            return redirect(url_for('login'))
        text = request.form['text']
        ip_address = request.remote_addr
        new_comment = Comment(text=text, ip_address=ip_address, user_id=current_user.id, message_id=message.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully.', 'success')
        highlighted_comment_id = new_comment.id
        return redirect(url_for('message_detail', message_id=message.id, _anchor=f'comment-{highlighted_comment_id}'))
    return render_template('message_detail.html', message=message, highlighted_comment_id=highlighted_comment_id)

@app.route('/message/admin/<int:message_id>', methods=['GET', 'POST'])
@admin_required
def message_detail_admin(message_id):
    message = Message.query.get_or_404(message_id)
    highlighted_comment_id = None
    if request.method == 'POST':
        text = request.form['text']
        ip_address = request.remote_addr
        new_comment = Comment(text=text, ip_address=ip_address, user_id=current_user.id, message_id=message.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully.', 'success')
        highlighted_comment_id = new_comment.id
        return redirect(url_for('message_detail_admin', message_id=message.id, _anchor=f'comment-{highlighted_comment_id}'))
    return render_template('message_detail_admin.html', message=message, highlighted_comment_id=highlighted_comment_id)

@app.route('/videos')
def videos():
    return render_template('videos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('foro'))
        flash('Nombre de usuario o contraseña incorrectos')
    return render_template('login.html', title="Login")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title="Register")

@app.route('/admin')
@admin_required
def admin_dashboard():
    users = User.query.all()
    messages = Message.query.all()
    comments = Comment.query.all()
    return render_template('admin_dashboard.html', users=users, messages=messages, comments=comments, title="Admin Dashboard")

@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_post/<int:post_id>')
@admin_required
def admin_delete_post(post_id):
    post = Message.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully.')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_comment/<int:comment_id>')
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if comment:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully.')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
