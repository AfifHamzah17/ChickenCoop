# Gunakan Python runtime resmi sebagai image induk 
FROM python:3.9-slim 
# Tetapkan direktori kerja di kontainer 
WORKDIR /usr/src/app 
# Salin konten direktori saat ini ke kontainer di /usr/src/app 
COPY . . 
# Instal semua dependensi yang diperlukan yang ditentukan di requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt 
# Jadikan port 5000 tersedia untuk dunia luar kontainer ini 
EXPOSE 5000 
# Tetapkan variabel lingkungan 
ENV FLASK_APP=app.py 
# Jalankan app.py saat kontainer dilun
CMD ["flask", "run", "--host=0.0.0.0"]