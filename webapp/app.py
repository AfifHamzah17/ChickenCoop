from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import plotly.graph_objs as go
import plotly.io as pio
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan kunci rahasia Anda
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Model User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Endpoint untuk mengambil data dari Thingspeak
def get_thingspeak_data(api_key):
    url = f"https://api.thingspeak.com/channels/2669844/feeds.json?api_key={api_key}&results=2"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return {}
    return response.json()

# Fungsi untuk mengenkripsi data
def encrypt_data(data, key):
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data

# Fungsi untuk mendekripsi data
def decrypt_data(encrypted_data, key):
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data).decode()
    return decrypted_data

def create_chart(x_data, y_data, title):
    fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='lines+markers')])
    fig.update_layout(title=title, xaxis_title='Time', yaxis_title='Value')
    img = BytesIO()
    pio.write_image(fig, img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

@app.route('/')
@login_required
def index():
    api_key = '{your_api_key}'
    data = get_thingspeak_data(api_key)
    
    # Check and print the response for debugging
    print(data)

    if 'feeds' in data and data['feeds']:
        feeds = data['feeds']
        
        # Prepare data for charts
        timestamps = [feed['created_at'] for feed in feeds]
        field1_data = [float(feed.get('field1', 0)) if feed.get('field1x') is not None else 0 for feed in feeds]
        field2_data = [float(feed.get('field2', 0)) if feed.get('field2') is not None else 0 for feed in feeds]
        field3_data = [float(feed.get('field3', 0)) if feed.get('field3') is not None else 0 for feed in feeds]
        field4_data = [float(feed.get('field4', 0)) if feed.get('field4') is not None else 0 for feed in feeds]
        # field3_data = [float(feed.get('field3', 0)) for feed in feeds]
        # field4_data = [float(feed.get('field4', 0)) for feed in feeds]
        
        # Generate a key for encryption
        key1 = Fernet.generate_key()
        key2 = Fernet.generate_key()
        key3 = Fernet.generate_key()
        key4 = Fernet.generate_key()

        # Encrypt the data using the generated keys
        encrypted_field1 = encrypt_data(str(field1_data), key1)
        encrypted_field2 = encrypt_data(str(field2_data), key2)
        encrypted_field3 = encrypt_data(str(field3_data), key3)
        encrypted_field4 = encrypt_data(str(field4_data), key4)

        # Create charts for the fields
        img1 = create_chart(timestamps, field1_data, 'Field 1 Chart')
        img2 = create_chart(timestamps, field2_data, 'Field 2 Chart')
        img3 = create_chart(timestamps, field3_data, 'Field 3 Chart')
        img4 = create_chart(timestamps, field4_data, 'Field 4 Chart')

        return render_template('index.html', 
                               encrypted_field1=encrypted_field1.decode(), 
                               encrypted_field2=encrypted_field2.decode(),
                               encrypted_field3=encrypted_field3.decode(),
                               encrypted_field4=encrypted_field4.decode(),
                               img1=img1,
                               img2=img2,
                               img3=img3,
                               img4=img4)
    else:
        return "No data found or invalid API key."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
