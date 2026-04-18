import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, g, jsonify
import openai

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ OpenAI API Key
openai.api_key = "sk-..."

# Database path
DATABASE = 'salarynow.db'


# ---------- DB Connection ----------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS salary_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount TEXT,
            reason TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')
        db.commit()


def create_tables():
    conn = sqlite3.connect('salarynow.db')
    c = conn.cursor()

    # Create requests table
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            amount REAL NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Run it once to set up
create_tables()


# ---------- Routes ----------
@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "⚠️ Username already exists."
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            session['username'] = user['username']
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return "❌ Invalid credentials."
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        amount = request.form['amount']
        reason = request.form['reason']
        db.execute("INSERT INTO salary_requests (user_id, amount, reason, status) VALUES (?, ?, ?, ?)",
                   (session['user_id'], amount, reason, 'Pending'))
        db.commit()

    requests = db.execute("SELECT * FROM salary_requests WHERE user_id=? ORDER BY id DESC",
                          (session['user_id'],)).fetchall()

    return render_template('dashboard.html', username=session['username'], requests=requests)

@app.route('/request', methods=['POST'])
def handle_request():
    if 'username' not in session:
        return redirect('/login')

    amount = request.form.get('amount')
    reason = request.form.get('reason')

    db = get_db()
    db.execute(
        'INSERT INTO salary_requests (user_id, amount, reason, status) VALUES (?, ?, ?, ?)',
        (session['user_id'], amount, reason, 'Pending')
    )
    db.commit()

    return redirect('/dashboard')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------- Admin ----------
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')


@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin-login')

    db = get_db()
    c = db.cursor()
    c.execute('''
        SELECT salary_requests.id, users.username, salary_requests.amount, salary_requests.reason, salary_requests.status
        FROM salary_requests
        JOIN users ON salary_requests.user_id = users.id
    ''')
    requests = [{
        'id': row[0],
        'username': row[1],
        'amount': row[2],
        'reason': row[3],
        'status': row[4]
    } for row in c.fetchall()]

    return render_template('admin_dashboard.html', requests=requests)


@app.route('/admin/action/<int:req_id>/<string:decision>')
def admin_action(req_id, decision):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    db = get_db()
    new_status = 'Approved' if decision == 'approve' else 'Rejected'
    db.execute("UPDATE salary_requests SET status=? WHERE id=?", (new_status, req_id))
    db.commit()

    return redirect(url_for('admin_dashboard'))


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin-login')


# ---------- AI Chat ----------
@app.route("/ai", methods=["POST"])
def ai_response():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"response": "Please enter a message."})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a salary request website."},
                {"role": "user", "content": user_input}
            ]
        )
        answer = response['choices'][0]['message']['content']
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)}"})


# ---------- Run ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
