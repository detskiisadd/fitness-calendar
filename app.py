from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS workouts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, workout TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS meals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, meal TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_workout', methods=['POST'])
def add_workout():
    data = request.json
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    c.execute("INSERT INTO workouts (date, workout) VALUES (?, ?)", (data['date'], data['workout']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Training hinzugefügt"})

@app.route('/add_meal', methods=['POST'])
def add_meal():
    data = request.json
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    c.execute("INSERT INTO meals (date, meal) VALUES (?, ?)", (data['date'], data['meal']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Mahlzeit hinzugefügt"})

@app.route('/get_entries', methods=['GET'])
def get_entries():
    date = request.args.get('date')
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    c.execute("SELECT workout FROM workouts WHERE date = ?", (date,))
    workouts = c.fetchall()
    c.execute("SELECT meal FROM meals WHERE date = ?", (date,))
    meals = c.fetchall()
    conn.close()
    return jsonify({"workouts": [w[0] for w in workouts], "meals": [m[0] for m in meals]})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)