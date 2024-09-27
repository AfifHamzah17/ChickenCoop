import sqlite3

# Buat koneksi ke database (akan dibuat jika belum ada)
conn = sqlite3.connect('database.db')

# Buat cursor untuk berinteraksi dengan database
cursor = conn.cursor()

# Buat tabel untuk menyimpan data sensor
cursor.execute('''
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    current REAL NOT NULL,
    power REAL NOT NULL,
    solar REAL NOT NULL,
    temperature REAL NOT NULL
)
''')

# Commit perubahan dan tutup koneksi
conn.commit()
conn.close()
