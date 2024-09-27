from app import app, db, User  # Pastikan mengimpor app
from werkzeug.security import generate_password_hash

# Buat objek pengguna baru
username = 'admin'  # Ganti dengan username yang diinginkan
password = 'password123'
# Hash password menggunakan metode default
hashed_password = generate_password_hash(password)

# Buat pengguna baru
new_user = User(username=username, password=hashed_password)

# Membuat aplikasi konteks untuk database
with app.app_context():
    # Tambahkan pengguna ke database
    db.session.add(new_user)
    db.session.commit()

print(f'User {username} has been created.')
