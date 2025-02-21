# app.py ist die Hauptdatei, die die gesamte Logik für die Anwendung enthält.
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'WUHaJMZ7NSXCWbzmog4Zs1PbyqCpf3vr'

# Datenbank-Verbindung
def get_db():
    conn = sqlite3.connect('gym_notes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialisierung der Datenbank
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trainings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                training_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                weight INTEGER NOT NULL,
                type TEXT,
                FOREIGN KEY(training_id) REFERENCES trainings(id)
            )
        ''')

# Startseite 
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Registrierung
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        with get_db() as conn:
            try:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                return redirect('/')
            except sqlite3.IntegrityError:
                return 'Benutzername bereits vergeben'

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                return redirect('/track')
            else:
                return 'Falsche Anmeldedaten'

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Track
@app.route('/track')
def track():
    if 'user_id' not in session:
        return redirect('/')

    return render_template('track.html')

# Trainingseinheit hinzufügen
@app.route('/add_training', methods=['POST'])
def add_training():
    if 'user_id' not in session:
        return redirect('/')

    date = request.form['trainingDate']
    with get_db() as conn:
        conn.execute('''
            INSERT INTO trainings (user_id, date)
            VALUES (?, ?)
        ''', (session['user_id'], date))
        training_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

    return redirect(url_for('add_exercise', training_id=training_id))

# Übung hinzufügen
@app.route('/add_exercise/<int:training_id>', methods=['GET', 'POST'])
def add_exercise(training_id):
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        name = request.form['name']
        sets = request.form['sets']
        reps = request.form['reps']
        weight = request.form['weight']
        type = request.form['type']
        with get_db() as conn:
            conn.execute('''
                INSERT INTO exercises (training_id, name, sets, reps, weight, type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (training_id, name, sets, reps, weight, type))

        return redirect(url_for('history'))

    return render_template('add-exercise.html', training_id=training_id)

# Übungen hinzufügen
@app.route('/add_exercises/<int:training_id>', methods=['POST'])
def add_exercises(training_id):
    if 'user_id' not in session:
        return redirect('/')

    data = request.get_json()
    exercises = data['exercises']
    with get_db() as conn:
        for exercise in exercises:
            conn.execute('''
                INSERT INTO exercises (training_id, name, sets, reps, weight, type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (training_id, exercise['name'], exercise['sets'], exercise['reps'], exercise['weight'], exercise['type']))

    return jsonify({'success': True})

# Übung löschen
@app.route('/delete_exercise/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    if 'user_id' not in session:
        return redirect('/')

    with get_db() as conn:
        conn.execute('DELETE FROM exercises WHERE id = ?', (id,))

    return jsonify({'status': 'deleted'})

# Übung bearbeiten
@app.route('/update_exercise/<int:exercise_id>', methods=['POST'])
def update_exercise(exercise_id):
    if 'user_id' not in session:
        return redirect('/')

    data = request.get_json()
    field = data['field']
    value = data['value']
    with get_db() as conn:
        conn.execute(f'UPDATE exercises SET {field} = ? WHERE id = ?', (value, exercise_id))
    return jsonify({'success': True})

# Training löschen
@app.route('/delete_training/<int:training_id>', methods=['POST'])
def delete_training(training_id):
    if 'user_id' not in session:
        return redirect('/')

    with get_db() as conn:
        conn.execute('DELETE FROM trainings WHERE id = ?', (training_id,))
        conn.execute('DELETE FROM exercises WHERE training_id = ?', (training_id,))

    return jsonify({'success': True})

# History
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/')

    with get_db() as conn:
        trainings = conn.execute('SELECT * FROM trainings WHERE user_id = ?', (session['user_id'],)).fetchall()
        trainings = [dict(training) for training in trainings]  
        for training in trainings:
            training['exercises'] = conn.execute('SELECT * FROM exercises WHERE training_id = ?', (training['id'],)).fetchall()
            training['exercises'] = [dict(exercise) for exercise in training['exercises']]  

    # 
    trainings = [training for training in trainings if training['exercises']]

    return render_template('history.html', trainings=trainings)

# Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)