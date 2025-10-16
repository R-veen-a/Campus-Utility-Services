from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from datetime import datetime, timedelta
import json
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configure upload folder for photos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database initialization
def init_db():
    conn = sqlite3.connect('campus.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Rooms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL,
            capacity INTEGER,
            room_type TEXT,
            status TEXT DEFAULT 'available'
        )
    ''')
    
    # Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            user_id INTEGER,
            booking_date DATE,
            start_time TIME,
            end_time TIME,
            purpose TEXT,
            status TEXT DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Issues table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            description TEXT,
            location TEXT,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Teacher availability table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            day_of_week TEXT,
            start_time TIME,
            end_time TIME,
            status TEXT DEFAULT 'available',
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # Bus routes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bus_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_name TEXT,
            departure_time TIME,
            destination TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Canteen menu table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS canteen_menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week TEXT,
            meal_type TEXT,
            item_name TEXT,
            price REAL,
            available BOOLEAN DEFAULT 1
        )
    ''')
    
    # Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            message TEXT,
            category TEXT,
            read_status BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Washroom status table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS washroom_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            status TEXT DEFAULT 'clean',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            event_date DATE,
            event_time TIME,
            location TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Camera feeds table for seat availability
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS camera_feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            feed_url TEXT,
            status TEXT DEFAULT 'active',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # AI voice alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            threshold DECIMAL(5,2),
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Maintenance photos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_id INTEGER,
            photo_path TEXT NOT NULL,
            uploaded_by INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (issue_id) REFERENCES issues (id),
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )
    ''')
    
    # Insert sample data
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, email) VALUES (?, ?, ?, ?)',
                  ('admin', generate_password_hash('admin123'), 'admin', 'admin@campus.com'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, email) VALUES (?, ?, ?, ?)',
                  ('student1', generate_password_hash('student123'), 'student', 'student1@campus.com'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, email) VALUES (?, ?, ?, ?)',
                  ('faculty1', generate_password_hash('faculty123'), 'faculty', 'faculty1@campus.com'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, email) VALUES (?, ?, ?, ?)',
                  ('chef1', generate_password_hash('chef123'), 'chef', 'chef1@campus.com'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, email) VALUES (?, ?, ?, ?)',
                  ('buscoord1', generate_password_hash('bus123'), 'buscoordinator', 'buscoord1@campus.com'))
    
    # Insert sample rooms
    rooms_data = [
        ('Room 101', 30, 'classroom', 'available'),
        ('Room 102', 25, 'classroom', 'available'),
        ('Lab A', 20, 'laboratory', 'available'),
        ('Library', 50, 'library', 'available'),
        ('Conference Room', 15, 'conference', 'available')
    ]
    cursor.executemany('INSERT OR IGNORE INTO rooms (room_name, capacity, room_type, status) VALUES (?, ?, ?, ?)', rooms_data)
    
    # Insert sample bus routes
    bus_routes = [
        ('Route 1', '08:00', 'Downtown', 'active'),
        ('Route 2', '08:30', 'Suburb', 'active'),
        ('Route 3', '17:00', 'Downtown', 'active')
    ]
    cursor.executemany('INSERT OR IGNORE INTO bus_routes (route_name, departure_time, destination, status) VALUES (?, ?, ?, ?)', bus_routes)
    
    # Insert sample washroom status
    washrooms = [
        ('Block A - Ground Floor', 'clean'),
        ('Block B - First Floor', 'clean'),
        ('Library', 'clean')
    ]
    cursor.executemany('INSERT OR IGNORE INTO washroom_status (location, status) VALUES (?, ?)', washrooms)
    
    # Insert sample canteen menu
    menu_items = [
        ('Monday', 'lunch', 'Vegetable Biryani', 120.0),
        ('Monday', 'dinner', 'Chicken Curry', 150.0),
        ('Tuesday', 'lunch', 'Masala Dosa', 80.0),
        ('Tuesday', 'dinner', 'Paneer Tikka', 130.0)
    ]
    cursor.executemany('INSERT OR IGNORE INTO canteen_menu (day_of_week, meal_type, item_name, price) VALUES (?, ?, ?, ?)', menu_items)
    
    # Insert sample issues
    sample_issues = [
        (1, 'washroom', 'Block A washroom needs cleaning', 'Block A', 'high'),
        (2, 'classroom', 'Projector not working in Room 101', 'Room 101', 'medium'),
        (3, 'food', 'Canteen food quality issue', 'Canteen', 'low'),
        (4, 'bus', 'Bus route 1 delayed', 'Bus Stop', 'high')
    ]
    cursor.executemany('INSERT OR IGNORE INTO issues (user_id, category, description, location, priority) VALUES (?, ?, ?, ?, ?)', sample_issues)
    
    # Insert sample bookings
    sample_bookings = [
        (1, 1, '2024-01-15', '09:00', '11:00', 'Class meeting'),
        (2, 2, '2024-01-16', '14:00', '16:00', 'Study group'),
        (3, 3, '2024-01-17', '10:00', '12:00', 'Lab session')
    ]
    cursor.executemany('INSERT OR IGNORE INTO bookings (room_id, user_id, booking_date, start_time, end_time, purpose) VALUES (?, ?, ?, ?, ?, ?)', sample_bookings)
    
    # Insert sample notifications
    sample_notifications = [
        (1, 'System Alert', 'Library maintenance scheduled for tomorrow', 'system', 0),
        (2, 'Room Booking', 'Your room booking for Room 101 is confirmed', 'booking', 0),
        (3, 'Issue Update', 'Your reported issue has been resolved', 'issue', 0)
    ]
    cursor.executemany('INSERT OR IGNORE INTO notifications (user_id, title, message, category, read_status) VALUES (?, ?, ?, ?, ?)', sample_notifications)
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

def get_db_connection():
    conn = sqlite3.connect('campus.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = session['role']
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'student':
        return redirect(url_for('student_dashboard'))
    elif role == 'faculty':
        return redirect(url_for('faculty_dashboard'))
    elif role == 'chef':
        return redirect(url_for('chef_dashboard'))
    elif role == 'buscoordinator':
        return redirect(url_for('buscoordinator_dashboard'))
    
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    
    # Handle empty tables with LEFT JOIN to avoid errors
    try:
        issues = conn.execute('SELECT i.*, u.username FROM issues i LEFT JOIN users u ON i.user_id = u.id').fetchall()
    except:
        issues = []
    
    try:
        bookings = conn.execute('SELECT b.*, r.room_name, u.username FROM bookings b LEFT JOIN rooms r ON b.room_id = r.id LEFT JOIN users u ON b.user_id = u.id').fetchall()
    except:
        bookings = []
    
    conn.close()
    
    return render_template('admin_dashboard.html', users=users, issues=issues, bookings=bookings, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    available_rooms = conn.execute('SELECT * FROM rooms WHERE status = "available"').fetchall()
    
    try:
        notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 10', (session['user_id'],)).fetchall()
    except:
        notifications = []
    
    bus_routes = conn.execute('SELECT * FROM bus_routes WHERE status = "active"').fetchall()
    
    try:
        canteen_menu = conn.execute('SELECT * FROM canteen_menu WHERE day_of_week = ? AND available = 1', (datetime.now().strftime('%A'),)).fetchall()
    except:
        canteen_menu = []
    
    conn.close()
    
    return render_template('student_dashboard.html', 
                         available_rooms=available_rooms, 
                         notifications=notifications,
                         bus_routes=bus_routes,
                         canteen_menu=canteen_menu)

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'user_id' not in session or session['role'] != 'faculty':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    teacher_availability = conn.execute('SELECT * FROM teacher_availability WHERE teacher_id = ?', (session['user_id'],)).fetchall()
    notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 10', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('faculty_dashboard.html', 
                         teacher_availability=teacher_availability,
                         notifications=notifications)

@app.route('/chef/dashboard')
def chef_dashboard():
    if 'user_id' not in session or session['role'] != 'chef':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    canteen_menu = conn.execute('SELECT * FROM canteen_menu ORDER BY day_of_week, meal_type').fetchall()
    notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 10', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('chef_dashboard.html', 
                         canteen_menu=canteen_menu,
                         notifications=notifications)

@app.route('/buscoordinator/dashboard')
def buscoordinator_dashboard():
    if 'user_id' not in session or session['role'] != 'buscoordinator':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    bus_routes = conn.execute('SELECT * FROM bus_routes').fetchall()
    issues = conn.execute('SELECT i.*, u.username FROM issues i JOIN users u ON i.user_id = u.id WHERE i.category = "bus"').fetchall()
    notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 10', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('buscoordinator_dashboard.html', 
                         bus_routes=bus_routes,
                         issues=issues,
                         notifications=notifications)

# Room booking routes
@app.route('/book_room', methods=['GET', 'POST'])
def book_room():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        room_id = request.form['room_id']
        booking_date = request.form['booking_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        purpose = request.form['purpose']
        
        conn = get_db_connection()
        
        # Check for booking conflicts
        existing_booking = conn.execute('''
            SELECT * FROM bookings 
            WHERE room_id = ? AND booking_date = ? 
            AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
        ''', (room_id, booking_date, start_time, start_time, end_time, end_time)).fetchone()
        
        if existing_booking:
            flash('Room is already booked for this time slot!', 'error')
        else:
            conn.execute('''
                INSERT INTO bookings (room_id, user_id, booking_date, start_time, end_time, purpose)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (room_id, session['user_id'], booking_date, start_time, end_time, purpose))
            conn.commit()
            flash('Room booked successfully!', 'success')
        
        conn.close()
        return redirect(url_for('book_room'))
    
    conn = get_db_connection()
    rooms = conn.execute('SELECT * FROM rooms WHERE status = "available"').fetchall()
    my_bookings = conn.execute('''
        SELECT b.*, r.room_name FROM bookings b 
        JOIN rooms r ON b.room_id = r.id 
        WHERE b.user_id = ? ORDER BY b.booking_date DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('book_room.html', rooms=rooms, my_bookings=my_bookings)

# Issue reporting routes
@app.route('/report_issue', methods=['GET', 'POST'])
def report_issue():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        location = request.form['location']
        priority = request.form['priority']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO issues (user_id, category, description, location, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], category, description, location, priority))
        conn.commit()
        conn.close()
        
        flash('Issue reported successfully!', 'success')
        return redirect(url_for('report_issue'))
    
    conn = get_db_connection()
    my_issues = conn.execute('''
        SELECT * FROM issues WHERE user_id = ? ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('report_issue.html', my_issues=my_issues)

# Teacher availability routes
@app.route('/teacher_availability', methods=['GET', 'POST'])
def teacher_availability():
    if 'user_id' not in session or session['role'] not in ['faculty', 'student', 'admin']:
        return redirect(url_for('login'))
    
    if request.method == 'POST' and session['role'] == 'faculty':
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        status = request.form['status']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT OR REPLACE INTO teacher_availability (teacher_id, day_of_week, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], day_of_week, start_time, end_time, status))
        conn.commit()
        conn.close()
        
        flash('Availability updated successfully!', 'success')
        return redirect(url_for('teacher_availability'))
    
    conn = get_db_connection()
    if session['role'] == 'faculty':
        # Faculty can see their own availability
        availability = conn.execute('''
            SELECT * FROM teacher_availability WHERE teacher_id = ? ORDER BY day_of_week
        ''', (session['user_id'],)).fetchall()
    else:
        # Students and admin can see all faculty availability
        availability = conn.execute('''
            SELECT ta.*, u.username FROM teacher_availability ta 
            JOIN users u ON ta.teacher_id = u.id 
            WHERE u.role = 'faculty' 
            ORDER BY u.username, ta.day_of_week
        ''').fetchall()
    conn.close()
    
    return render_template('teacher_availability.html', availability=availability)

# Canteen menu routes
@app.route('/canteen_menu', methods=['GET', 'POST'])
def canteen_menu():
    if 'user_id' not in session or session['role'] not in ['chef', 'admin']:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        day_of_week = request.form['day_of_week']
        meal_type = request.form['meal_type']
        item_name = request.form['item_name']
        price = request.form['price']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO canteen_menu (day_of_week, meal_type, item_name, price)
            VALUES (?, ?, ?, ?)
        ''', (day_of_week, meal_type, item_name, price))
        conn.commit()
        conn.close()
        
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('canteen_menu'))
    
    conn = get_db_connection()
    menu_items = conn.execute('SELECT * FROM canteen_menu ORDER BY day_of_week, meal_type').fetchall()
    conn.close()
    
    return render_template('canteen_menu.html', menu_items=menu_items)

# Bus routes routes
@app.route('/bus_routes', methods=['GET', 'POST'])
def bus_routes():
    if 'user_id' not in session or session['role'] != 'buscoordinator':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        route_name = request.form['route_name']
        departure_time = request.form['departure_time']
        destination = request.form['destination']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO bus_routes (route_name, departure_time, destination)
            VALUES (?, ?, ?)
        ''', (route_name, departure_time, destination))
        conn.commit()
        conn.close()
        
        flash('Bus route added successfully!', 'success')
        return redirect(url_for('bus_routes'))
    
    conn = get_db_connection()
    routes = conn.execute('SELECT * FROM bus_routes ORDER BY departure_time').fetchall()
    conn.close()
    
    return render_template('bus_routes.html', routes=routes)

# Washroom status routes
@app.route('/washroom_status', methods=['GET', 'POST'])
def washroom_status():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        location = request.form['location']
        status = request.form['status']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT OR REPLACE INTO washroom_status (location, status)
            VALUES (?, ?)
        ''', (location, status))
        conn.commit()
        conn.close()
        
        flash('Washroom status updated successfully!', 'success')
        return redirect(url_for('washroom_status'))
    
    conn = get_db_connection()
    washrooms = conn.execute('SELECT * FROM washroom_status ORDER BY location').fetchall()
    conn.close()
    
    return render_template('washroom_status.html', washrooms=washrooms)

# API routes for AJAX calls
@app.route('/api/notifications')
def get_notifications():
    if 'user_id' not in session:
        return jsonify([])
    
    conn = get_db_connection()
    notifications = conn.execute('''
        SELECT * FROM notifications WHERE user_id = ? AND read_status = 0 
        ORDER BY created_at DESC LIMIT 5
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return jsonify([dict(n) for n in notifications])

@app.route('/api/mark_notification_read/<int:notification_id>')
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    conn = get_db_connection()
    conn.execute('UPDATE notifications SET read_status = 1 WHERE id = ? AND user_id = ?', 
                (notification_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Camera access for seat availability
@app.route('/camera_access')
def camera_access():
    if 'user_id' not in session or session['role'] not in ['student', 'faculty', 'admin']:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    camera_feeds = conn.execute('SELECT * FROM camera_feeds WHERE status = "active"').fetchall()
    conn.close()
    
    return render_template('camera_access.html', camera_feeds=camera_feeds)

# Clear all menu items
@app.route('/clear_all_menu', methods=['POST'])
def clear_all_menu():
    if 'user_id' not in session or session['role'] not in ['chef', 'admin']:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM canteen_menu')
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# AI voice alerts for library silence
@app.route('/ai_alerts')
def ai_alerts():
    if 'user_id' not in session or session['role'] not in ['admin', 'faculty']:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    alerts = conn.execute('SELECT * FROM ai_alerts ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('ai_alerts.html', alerts=alerts)

# Delete functionality for all items
@app.route('/delete/<item_type>/<int:item_id>')
def delete_item(item_type, item_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    
    try:
        if item_type == 'user':
            conn.execute('DELETE FROM users WHERE id = ?', (item_id,))
        elif item_type == 'issue':
            conn.execute('DELETE FROM issues WHERE id = ?', (item_id,))
        elif item_type == 'booking':
            conn.execute('DELETE FROM bookings WHERE id = ?', (item_id,))
        elif item_type == 'menu':
            conn.execute('DELETE FROM canteen_menu WHERE id = ?', (item_id,))
        elif item_type == 'route':
            conn.execute('DELETE FROM bus_routes WHERE id = ?', (item_id,))
        elif item_type == 'washroom':
            conn.execute('DELETE FROM washroom_status WHERE id = ?', (item_id,))
        
        conn.commit()
        flash(f'{item_type.title()} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting {item_type}: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(request.referrer or url_for('dashboard'))

# Photo upload for washroom maintenance
@app.route('/upload_photo/<int:issue_id>', methods=['GET', 'POST'])
def upload_photo(issue_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"maintenance_{issue_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO maintenance_photos (issue_id, photo_path, uploaded_by)
                VALUES (?, ?, ?)
            ''', (issue_id, filename, session['user_id']))
            conn.commit()
            conn.close()
            
            flash('Photo uploaded successfully!', 'success')
            return redirect(url_for('report_issue'))
    
    conn = get_db_connection()
    issue = conn.execute('SELECT * FROM issues WHERE id = ?', (issue_id,)).fetchone()
    photos = conn.execute('SELECT * FROM maintenance_photos WHERE issue_id = ?', (issue_id,)).fetchall()
    conn.close()
    
    return render_template('upload_photo.html', issue=issue, photos=photos)

# API for camera feed status
@app.route('/api/camera_status')
def camera_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    conn = get_db_connection()
    feeds = conn.execute('SELECT * FROM camera_feeds WHERE status = "active"').fetchall()
    conn.close()
    
    return jsonify([dict(feed) for feed in feeds])

# API for AI alert status
@app.route('/api/ai_alert_status')
def ai_alert_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    conn = get_db_connection()
    alerts = conn.execute('SELECT * FROM ai_alerts WHERE status = "active"').fetchall()
    conn.close()
    
    return jsonify([dict(alert) for alert in alerts])

if __name__ == '__main__':
    app.run(debug=True) 