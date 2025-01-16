from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from cryptography.fernet import Fernet
import requests
import plotly.graph_objs as go
import plotly.io as pio
import base64
from io import BytesIO
from datetime import datetime
import pytz
from flask_socketio import SocketIO, emit

# Inisialisasi aplikasi
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan kunci rahasia Anda
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Inisialisasi SocketIO
socketio = SocketIO(app)

# Model User untuk autentikasi
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Endpoint untuk mengambil data dari Thingspeak
def get_thingspeak_data(api_key):
    url = f"https://api.thingspeak.com/channels/2681262/feeds.json?api_key={api_key}&results=2"
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

# Fungsi untuk membuat chart menggunakan Plotly
def create_chart(x_data, y_data, title):
    try:
        fig = go.Figure(data=[go.Scatter(x=x_data, y=y_data, mode='lines+markers')])
        fig.update_layout(title=title, xaxis_title='Time', yaxis_title='Value')
        img = BytesIO()
        pio.write_image(fig, img, format='png')
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()  # Mengembalikan base64 yang valid
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None  # Menangani error jika pembuatan gambar gagal

# Fungsi untuk mengonversi waktu UTC ke waktu lokal
def convert_utc_to_local(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_zone = pytz.utc
    local_zone = pytz.timezone("Asia/Jakarta")  # Zona waktu Indonesia Barat
    utc_time = utc_zone.localize(utc_time)
    local_time = utc_time.astimezone(local_zone)
    return local_time.strftime("%Y-%m-%d %H:%M:%S")

# Route utama
@app.route('/')
@login_required
def index():
    api_key = '8BZFNOBEHDUYIC4Z'
    data = get_thingspeak_data(api_key)

    if 'feeds' in data and data['feeds']:
        feeds = data['feeds']
        timestamps = [convert_utc_to_local(feed['created_at']) for feed in feeds]
        field1_data = [float(feed.get('field1', 0)) for feed in feeds]
        field2_data = [float(feed.get('field2', 0)) for feed in feeds]
        field3_data = [float(feed.get('field3', 0)) for feed in feeds]
        field4_data = [float(feed.get('field4', 0)) for feed in feeds]

        # Membuat gambar untuk chart
        img1 = create_chart(timestamps, field1_data, 'Field 1 Chart')
        img2 = create_chart(timestamps, field2_data, 'Field 2 Chart')
        img3 = create_chart(timestamps, field3_data, 'Field 3 Chart')
        img4 = create_chart(timestamps, field4_data, 'Field 4 Chart')

        # Emit gambar dan data ke frontend menggunakan SocketIO
        socketio.emit('update_chart', {
            'img1': img1,
            'img2': img2,
            'img3': img3,
            'img4': img4,
            'timestamps': timestamps,
            'field1_data': field1_data,
            'field2_data': field2_data,
            'field3_data': field3_data,
            'field4_data': field4_data
        })

        return render_template('index.html', 
                               encrypted_field1=encrypt_data(str(field1_data), Fernet.generate_key()).decode(), 
                               encrypted_field2=encrypt_data(str(field2_data), Fernet.generate_key()).decode(),
                               encrypted_field3=encrypt_data(str(field3_data), Fernet.generate_key()).decode(),
                               encrypted_field4=encrypt_data(str(field4_data), Fernet.generate_key()).decode(),
                               img1=img1,
                               img2=img2,
                               img3=img3,
                               img4=img4)

# Route login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

# Route logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Fungsi untuk menangani koneksi SocketIO
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update_chart', {'message': 'Connected to the server'})

# Menjalankan aplikasi
if __name__ == '__main__':
    # Cloud Run automatically sets the PORT variable
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Membuat database jika belum ada
#     socketio.run(app, debug=True)
