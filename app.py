from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'petcheck_secret_2024')

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    url = urlparse(DATABASE_URL)
    return psycopg2.connect(
        host=url.hostname,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        port=url.port
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'pet_owner',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS pets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                species VARCHAR(50) NOT NULL,
                breed VARCHAR(100),
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS diagnoses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                image_path VARCHAR(255),
                predicted_disease VARCHAR(200),
                confidence FLOAT,
                advice TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS vets (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                clinic_name VARCHAR(200),
                phone VARCHAR(20),
                email VARCHAR(150),
                location VARCHAR(255),
                specialization VARCHAR(200),
                available BOOLEAN DEFAULT TRUE
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS forum_posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                title VARCHAR(255) NOT NULL,
                body TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS forum_replies (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL,
                user_id INTEGER,
                body TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES forum_posts(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        cur.execute("SELECT COUNT(*) FROM vets")
        if cur.fetchone()[0] == 0:
            cur.execute('''
                INSERT INTO vets (name, clinic_name, phone, email, location, specialization, available) VALUES
                ('Dr. Ssali James', 'Entebbe Veterinary Clinic', '+256700123456', 'james.ssali@vetclinic.ug', 'Division A, Entebbe', 'Dogs & Cats', TRUE),
                ('Dr. Nakato Sarah', 'PetCare Entebbe', '+256782654321', 'sarah.nakato@petcare.ug', 'Division B, Entebbe', 'Small Animals', TRUE),
                ('Dr. Mukasa David', 'Animal Health Center', '+256755987654', 'david.mukasa@animalhealth.ug', 'Kampala Rd, Entebbe', 'General Veterinary', TRUE)
            ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized!")
    except Exception as e:
        print(f"DB init error: {e}")

init_db()

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_user():
    if 'user_id' not in session:
        return None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, name, email, role FROM users WHERE id = %s", (session['user_id'],))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return {'id': row['id'], 'name': row['name'], 'email': row['email'], 'role': row['role']}
    except Exception:
        pass
    return None

def predict_disease(image_path):
    diseases = ["Healthy", "Skin Infection", "Eye Infection", "Ear Infection", "Ringworm", "Wounds/Injuries", "Obesity", "Dental Disease"]
    advice = {
        "Healthy": "✅ Your pet appears healthy!\n\n📋 Recommendations:\n• Schedule regular vet checkups\n• Maintain a balanced diet\n• Ensure daily exercise",
        "Skin Infection": "⚠️ SKIN INFECTION\n\n📋 Clean the area with mild soap. See a vet within 24-48 hours.",
        "Eye Infection": "⚠️ EYE INFECTION\n\n📋 Gently wipe discharge. See a vet within 24 hours.",
        "Ear Infection": "⚠️ EAR INFECTION\n\n📋 Do NOT insert anything. See a vet within 24-48 hours.",
        "Ringworm": "⚠️ RINGWORM\n\n📋 Isolate your pet. See a vet for antifungal medication.",
        "Wounds/Injuries": "🚨 WOUND DETECTED\n\n📋 Clean with saline. See a vet immediately if bleeding.",
        "Obesity": "⚠️ OBESITY\n\n📋 Reduce food portions. Increase exercise. Consult a vet.",
        "Dental Disease": "⚠️ DENTAL DISEASE\n\n📋 Brush teeth daily. Schedule dental cleaning."
    }
    disease = random.choice(diseases)
    confidence = random.randint(70, 90)
    return {
        'success': True,
        'disease': disease,
        'confidence': confidence,
        'advice': advice.get(disease, "Consult a veterinarian."),
        'all_predictions': [{'disease': disease, 'confidence': confidence}],
        'mode': 'render_demo'
    }

@app.route('/')
def home():
    return render_template('index.html', user=get_user())

@app.route('/upload')
def upload():
    return render_template('upload.html', user=get_user())

@app.route('/results')
def results():
    return render_template('results.html', result=session.get('last_result'), user=get_user())

@app.route('/vets')
def vets():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM vets WHERE available = TRUE")
        vets_list = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        vets_list = []
    return render_template('vets.html', vets=vets_list, user=get_user())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'pet_owner')
        if not name or not email or not password:
            return render_template('register.html', error='All fields are required.')
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters.')
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                cur.close()
                conn.close()
                return render_template('register.html', error='Account already exists.')
            hashed = generate_password_hash(password)
            cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
                       (name, email, hashed, role))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('login', success='Account created! Please log in.'))
        except Exception as e:
            return render_template('register.html', error=f'Database error: {str(e)}')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    success_msg = request.args.get('success', '')
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            return render_template('login.html', error='Please enter email and password.')
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT id, name, email, password, role FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            if not user or not check_password_hash(user['password'], password):
                return render_template('login.html', error='Incorrect email or password.')
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            return redirect(url_for('profile'))
        except Exception as e:
            return render_template('login.html', error=f'Database error: {str(e)}')
    return render_template('login.html', success=success_msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    user = get_user()
    pets, diagnoses = [], []
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM pets WHERE user_id = %s", (session['user_id'],))
        pets = cur.fetchall()
        cur.execute("SELECT * FROM diagnoses WHERE user_id = %s ORDER BY created_at DESC LIMIT 10", (session['user_id'],))
        diagnoses = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('profile.html', user=user, pets=pets, diagnoses=diagnoses)

@app.route('/add-pet', methods=['POST'])
@login_required
def add_pet():
    name = request.form.get('name', '').strip()
    species = request.form.get('species', 'dog')
    breed = request.form.get('breed', '').strip()
    age = request.form.get('age', None)
    if name:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO pets (user_id, name, species, breed, age) VALUES (%s, %s, %s, %s, %s)",
                        (session['user_id'], name, species, breed or None, age or None))
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass
    return redirect(url_for('profile'))

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    filename = secure_filename(file.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    result = predict_disease(filepath)
    if session.get('user_id') and result.get('success'):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO diagnoses (user_id, image_path, predicted_disease, confidence, advice) VALUES (%s, %s, %s, %s, %s)",
                        (session['user_id'], filepath, result['disease'], result['confidence'], result['advice']))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"DB save error: {e}")
    session['last_result'] = result
    return jsonify(result)

@app.route('/articles')
def articles():
    articles_list = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM articles ORDER BY created_at DESC")
        articles_list = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('articles.html', articles=articles_list, user=get_user())

@app.route('/articles/<int:article_id>')
def article_detail(article_id):
    article = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM articles WHERE id = %s", (article_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            article = {'id': row['id'], 'title': row['title'], 'content': row['content'], 'category': row['category'], 
                      'date': row['created_at'].strftime('%d %b %Y') if row['created_at'] else '', 'read_time': 4}
    except Exception:
        pass
    return render_template('article_detail.html', article=article, user=get_user())

@app.route('/forum')
def forum():
    posts = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT p.id, p.user_id, p.title, p.body, p.created_at,
                   COALESCE(u.name, 'Anonymous') as author_name,
                   (SELECT COUNT(*) FROM forum_replies WHERE post_id = p.id) as reply_count
            FROM forum_posts p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        """)
        posts = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        posts = []
    return render_template('forum.html', posts=posts, user=get_user())

@app.route('/forum/post', methods=['POST'])
@login_required
def forum_create_post():
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()
    if not title or not body:
        return redirect(url_for('forum'))
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO forum_posts (user_id, title, body) VALUES (%s, %s, %s)",
                    (session['user_id'], title, body))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
    return redirect(url_for('forum'))

@app.route('/forum/<int:post_id>')
def forum_detail(post_id):
    post = None
    replies = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT p.id, p.user_id, p.title, p.body, p.created_at,
                   COALESCE(u.name, 'Anonymous') as author_name
            FROM forum_posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
        """, (post_id,))
        post = cur.fetchone()
        cur.execute("""
            SELECT r.id, r.post_id, r.user_id, r.body, r.created_at,
                   COALESCE(u.name, 'Anonymous') as author_name,
                   COALESCE(u.role, 'pet_owner') as author_role
            FROM forum_replies r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.post_id = %s
            ORDER BY r.created_at ASC
        """, (post_id,))
        replies = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        pass
    return render_template('forum_detail.html', post=post, replies=replies, user=get_user())

@app.route('/forum/reply', methods=['POST'])
@login_required
def forum_create_reply():
    post_id = request.form.get('post_id')
    body = request.form.get('body', '').strip()
    if not post_id or not body:
        return redirect(url_for('forum'))
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO forum_replies (post_id, user_id, body) VALUES (%s, %s, %s)",
                    (post_id, session['user_id'], body))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
    return redirect(url_for('forum_detail', post_id=post_id))

@app.route('/test')
def test():
    return "PetCheck is running! 🐾"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)