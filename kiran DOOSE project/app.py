from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['ersonnel_management']

# Collections
employees_collection = db['employees']
admins_collection = db['admin']
modules_collection = db['modules']

# ---------- ROUTES ---------- #

@app.route('/')
def index():
    return render_template('index.html')

# ---------- EMPLOYEE REGISTER ---------- #
@app.route('/employee_register', methods=['GET', 'POST'])
def employee_register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        designation = request.form['designation']

        employees_collection.insert_one({
            "name": name,
            "username": username,
            "email": email,
            "password": password,
            "designation": designation,
            "login_time": "",
            "logout_time": "",
            "modules_completed": [],
            "modules_pending": [],
            "salary": 0  # Initialize salary
        })
        flash('Registration successful! Please log in.')
        return redirect(url_for('employee_login'))
    return render_template('employee_register.html')

# ---------- EMPLOYEE LOGIN ---------- #
@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        employee = employees_collection.find_one({'username': username, 'password': password})
        if employee:
            session['username'] = username
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            employees_collection.update_one({'username': username}, {'$set': {'login_time': login_time}})
            flash('Login successful!')
            return redirect(url_for('employee_dashboard'))
        else:
            flash('Invalid employee credentials!')
            return redirect(url_for('employee_login'))
    return render_template('employee_login.html')

# ---------- EMPLOYEE DASHBOARD ---------- #
@app.route('/employee_dashboard')
def employee_dashboard():
    if 'username' not in session:
        return redirect(url_for('employee_login'))

    employee = employees_collection.find_one({'username': session['username']})
    pending = employee.get('modules_pending', [])
    completed = employee.get('modules_completed', [])
    salary = employee.get('salary', 0)
    return render_template('employee_dashboard.html',
                           pending_modules=pending,
                           completed_modules=completed,
                           salary=salary)

# ---------- COMPLETE MODULE ---------- #
@app.route('/complete_module', methods=['POST'])
def complete_module():
    if 'username' not in session:
        return redirect(url_for('employee_login'))

    module_name = request.form['module_name']
    username = session['username']

    employee = employees_collection.find_one({'username': username})
    if module_name not in employee.get('modules_pending', []):
        return redirect(url_for('employee_dashboard'))

    # Update completed and pending lists and increment salary
    employees_collection.update_one(
        {'username': username},
        {
            '$pull': {'modules_pending': module_name},
            '$addToSet': {'modules_completed': module_name},
            '$inc': {'salary': 10000}  # Increment salary
        }
    )

    modules_collection.update_one(
        {'employee_username': username, 'module_name': module_name},
        {'$set': {'status': 'completed'}}
    )

    flash(f'Module "{module_name}" marked as completed!')
    return redirect(url_for('employee_dashboard'))

# ---------- DEBIT SALARY ---------- #
@app.route('/debit_salary', methods=['POST'])
def debit_salary():
    if 'username' not in session:
        return redirect(url_for('employee_login'))

    username = session['username']
    employees_collection.update_one(
        {'username': username},
        {'$set': {'salary': 0}}
    )
    flash('Salary has been debited to ₹0.')
    return redirect(url_for('employee_dashboard'))

# ---------- ADMIN LOGIN ---------- #
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = admins_collection.find_one({'username': username})
        if admin and admin['password'] == password:
            session['admin'] = username
            flash('Admin login successful!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

# ---------- ADMIN DASHBOARD ---------- #
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    employees = list(employees_collection.find({}, {
        '_id': 0,
        'username': 1,
        'name': 1,
        'email': 1,
        'designation': 1,
        'login_time': 1,
        'logout_time': 1,
        'modules_completed': 1,
        'modules_pending': 1,
        'salary': 1
    }))
    return render_template('admin_dashboard.html', employees=employees)

# ---------- ASSIGN MODULE TO EMPLOYEE ---------- #
@app.route('/assign_module/<username>', methods=['POST'])
def assign_module(username):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    module_name = request.form['module_name'].strip()
    if not module_name:
        flash("Module name cannot be empty.")
        return redirect(url_for('admin_dashboard'))

    modules_collection.insert_one({
        "employee_username": username,
        "module_name": module_name,
        "status": "pending"
    })

    employees_collection.update_one(
        {'username': username},
        {'$addToSet': {'modules_pending': module_name}}
    )

    flash(f'Module "{module_name}" assigned to {username}!')
    return redirect(url_for('admin_dashboard'))

# ---------- LOGOUT ---------- #
@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        employees_collection.update_one({'username': username}, {'$set': {'logout_time': logout_time}})
        flash('You have been logged out.')
    session.clear()
    return redirect(url_for('index'))

# ---------- RUN SERVER ---------- #
if __name__ == '__main__':
    app.run(debug=True)
