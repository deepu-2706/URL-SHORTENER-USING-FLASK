from flask import Flask, request, redirect, jsonify, render_template
import random
import string
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'root',
    'password': 'webstudent',
    'host': 'localhost',
    'database': 'deepu'
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form.get('long_url')
    if not long_url:
        return jsonify({'error': 'URL is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    short_code = generate_short_code()

    try:
        cursor.execute('INSERT INTO urls (long_url, short_code) VALUES (%s, %s)', (long_url, short_code))
        connection.commit()
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Failed to generate unique short code, please try again'}), 500
    finally:
        cursor.close()
        connection.close()

    return render_template('index2.html', short_url=request.host_url + short_code)

@app.route('/<short_code>', methods=['GET'])
def redirect_to_long_url(short_code):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT long_url FROM urls WHERE short_code = %s', (short_code,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result:
        return redirect(result[0])
    else:
        return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
