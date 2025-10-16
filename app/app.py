from flask import Flask, request, render_template
import mysql.connector
import boto3
from config import DB_CONFIG, S3_CONFIG
import uuid

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )

def upload_to_s3(file):
    s3 = boto3.client('s3', region_name=S3_CONFIG['region'])
    file_name = f"{uuid.uuid4()}_{file.filename}"
    s3.upload_fileobj(file, S3_CONFIG['bucket_name'], file_name)
    return f"https://{S3_CONFIG['bucket_name']}.s3.{S3_CONFIG['region']}.amazonaws.com/{file_name}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files['image']

        s3_url = upload_to_s3(file)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, image_url) VALUES (%s, %s)", (name, s3_url))
        conn.commit()
        cursor.close()
        conn.close()

        return f"Data saved! Image URL: {s3_url}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
