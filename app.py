from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

import requests

def get_motivation_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            return data[0]['q'] + " — " + data[0]['a']
        else:
            return "Stay positive, work hard, make it happen. — Unknown"
    except:
        return "Stay positive, work hard, make it happen. — Unknown"

@app.route('/tasks')
def home():
    print("SESSION:", session)
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            print("USER NOT FOUND")
            session.pop('username', None)
            return redirect(url_for('login'))

        tasks = Task.query.filter_by(user_id=user.id).order_by(
            db.case(
                (Task.category == 'Urgent', 1),
                (Task.category == 'Important', 2),
                (Task.category == 'Normal', 3),
                else_=4
            )
        ).all()

        quote = get_motivation_quote()
        return render_template('index.html', username=user.username, tasks=tasks, quote=quote)
    
    print("NO SESSION")
    return redirect(url_for('login'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' not in session:
        return redirect(url_for('login'))

    task_text = request.form['task_text']
    category = request.form['category']
    user = User.query.filter_by(username=session['username']).first()
    new_task = Task(text=task_text, completed=False, category=category, user_id=user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/toggle_complete/<int:task_id>')
def toggle_complete(task_id):
    task = Task.query.get(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    task = Task.query.get(task_id)
    new_text = request.form['new_text']
    task.text = new_text
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/search_tasks')
def search_tasks():
    keyword = request.args.get('q')
    user = User.query.filter_by(username=session['username']).first()
    tasks = Task.query.filter(Task.user_id==user.id, Task.text.like(f'%{keyword}%')).all()
    result = [{"id": t.id, "text": t.text, "completed": t.completed} for t in tasks]
    return jsonify(result)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash('Username and password cannot be empty!')
            return redirect(url_for('register'))

        if len(password) != 8:
            flash('Password must be exactly 8 characters!')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) > 8 or len(password) > 8:
            flash('Username and password max 8 characters!')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            return redirect(url_for('tasks'))
        else:
            flash('Invalid username or password!')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('dashboard'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
