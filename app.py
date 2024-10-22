import os
import csv
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar la aplicación Flask
app = Flask(__name__)
# Configurar la base de datos usando variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Inicializar la base de datos y las migraciones
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configuración de gestión de inicio de sesión
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Cargar usuario según su ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modelo de Usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='client')

# Modelo de Mensaje
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    signature = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

# Modelo de Comentario
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    message = db.relationship('Message', backref=db.backref('comments', lazy=True))

# Modelo de Reparto
class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(200), nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    items_delivered = db.Column(db.String(500), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('deliveries', lazy=True))

# Decorador para verificar roles específicos de usuarios
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Antes de cada solicitud, configurar si se muestra el enlace de administrador
@app.before_request
def before_request():
    g.show_admin_link = current_user.is_authenticated and current_user.role in ['developer', 'master']

# Ruta para la página principal
@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('home.html', title="Soderia Aparicio")

# Ruta para noticias
@app.route('/news')
def news():
    return render_template('news.html', title="Soderia Aparicio - Noticias")

# Ruta para el foro
@app.route('/foro')
def foro():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('foro.html', messages=messages, title="Foro")

# Ruta para postear en el foro
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

# Ruta para gestionar usuarios
@app.route('/gestion_usuarios', methods=['GET', 'POST'])
@login_required
@role_required(['developer', 'master'])
def gestion_usuarios():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User.query.get(user_id)
        if user:
            if 'role_developer' in request.form and current_user.role == 'developer':
                user.role = 'developer'
            elif 'role_master' in request.form and current_user.role in ['developer', 'master']:
                user.role = 'master'
            elif 'role_employee' in request.form and current_user.role in ['developer', 'master']:
                user.role = 'employee'
            elif 'role_client' in request.form:
                user.role = 'client'
            if 'email' in request.form:
                user.email = request.form['email']
            if 'phone_number' in request.form:
                user.phone_number = request.form['phone_number']
            db.session.commit()
            flash('Datos del usuario actualizados exitosamente.')
    users = User.query.all()
    return render_template('gestion_usuarios.html', users=users, title="Gestión de Usuarios")

# Ruta para gestionar repartos
@app.route('/gestion_repartos', methods=['GET', 'POST'])
@login_required
@role_required(['developer', 'master', 'employee'])
def gestion_repartos():
    if request.method == 'POST':
        delivery_id = request.form.get('delivery_id')
        if delivery_id:
            delivery = Delivery.query.get(delivery_id)
            if delivery:
                if 'client_name' in request.form:
                    delivery.client_name = request.form['client_name']
                if 'delivery_date' in request.form:
                    delivery.delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d')
                if 'items_delivered' in request.form:
                    delivery.items_delivered = request.form['items_delivered']
                if 'notes' in request.form:
                    delivery.notes = request.form['notes']
                db.session.commit()
                flash('Reparto actualizado exitosamente.')
        else:
            client_name = request.form['client_name']
            delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d')
            items_delivered = request.form['items_delivered']
            notes = request.form.get('notes', '')
            new_delivery = Delivery(client_name=client_name, delivery_date=delivery_date, items_delivered=items_delivered, notes=notes, user_id=current_user.id)
            db.session.add(new_delivery)
            db.session.commit()
            flash('Reparto creado exitosamente.')
    deliveries = Delivery.query.all()
    return render_template('gestion_repartos.html', deliveries=deliveries, title="Gestión de Repartos")

# Ruta para obtener extracto de cliente
@app.route('/cliente/extracto/<int:client_id>', methods=['GET', 'POST'])
@login_required
@role_required(['developer', 'master', 'employee'])
def obtener_extracto_cliente(client_id):
    client = User.query.get_or_404(client_id)
    deliveries = None

    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            deliveries = Delivery.query.filter(
                Delivery.client_name == client.username,
                Delivery.delivery_date >= fecha_inicio_dt,
                Delivery.delivery_date <= fecha_fin_dt
            ).all()

    return render_template('extracto_cliente.html', client=client, deliveries=deliveries)

# Ruta para descargar extracto de cliente en CSV
@app.route('/cliente/extracto/descargar/<int:client_id>', methods=['POST'])
@login_required
@role_required(['developer', 'master', 'employee'])
def descargar_extracto_cliente(client_id):
    client = User.query.get_or_404(client_id)
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    if not fecha_inicio or not fecha_fin:
        flash('Por favor ingrese ambas fechas.', 'danger')
        return redirect(url_for('obtener_extracto_cliente', client_id=client.id))

    # Convertir las fechas a objetos datetime
    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

    # Obtener los repartos del cliente en el rango de fechas
    deliveries = Delivery.query.filter(
        Delivery.client_name == client.username,
        Delivery.delivery_date >= fecha_inicio_dt,
        Delivery.delivery_date <= fecha_fin_dt
    ).all()

    # Verificar si hay datos para exportar
    if not deliveries:
        flash('No hay repartos disponibles en el rango de fechas seleccionado.', 'warning')
        return redirect(url_for('obtener_extracto_cliente', client_id=client.id))

    # Crear un archivo CSV con los datos obtenidos
    csv_path = f"/tmp/extracto_cliente_{client.username}_{fecha_inicio}_{fecha_fin}.csv"
    fieldnames = ['Fecha de Entrega', 'Ítems Entregados', 'Notas']

    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Escribir encabezados
        writer.writeheader()

        # Escribir los datos
        for delivery in deliveries:
            writer.writerow({
                'Fecha de Entrega': delivery.delivery_date.strftime('%Y-%m-%d'),
                'Ítems Entregados': delivery.items_delivered,
                'Notas': delivery.notes
            })

    # Enviar el archivo al cliente para su descarga
    return send_file(csv_path, as_attachment=True, download_name=f"Extracto_{client.username}_{fecha_inicio}_{fecha_fin}.csv")

# Ruta para iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Nombre de usuario o contraseña incorrectos')
    return render_template('login.html', title="Login")

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, phone_number=phone_number, password=hashed_password, role='client')

        db.session.add(new_user)
        db.session.commit()

        if new_user.role == 'employee':
            login_user(new_user)
            flash('Registro exitoso y has sido logueado automáticamente.', 'success')
            return redirect(url_for('home'))
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title="Register")

# Ruta para editar el perfil del usuario
@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        current_user.phone_number = request.form['phone_number']

        db.session.commit()
        flash('Perfil actualizado exitosamente.', 'success')
        return redirect(url_for('perfil'))

    return render_template('editar_perfil.html', user=current_user, title="Editar Perfil")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
