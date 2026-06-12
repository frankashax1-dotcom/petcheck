import pymysql
from werkzeug.security import generate_password_hash

# MySQL password
MYSQL_PASSWORD = "2026"

print("=" * 50)
print("👤 Adding Sample User...")
print("=" * 50)

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password=MYSQL_PASSWORD,
        database='petcheck',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = 'demo@petcheck.com'")
    if cursor.fetchone():
        print("⚠️  User already exists! Deleting old user...")
        cursor.execute("DELETE FROM users WHERE email = 'demo@petcheck.com'")
    
    # Create sample user
    name = "Demo User"
    email = "demo@petcheck.com"
    password = generate_password_hash("password123")
    role = "pet_owner"
    
    cursor.execute("""
        INSERT INTO users (name, email, password, role) 
        VALUES (%s, %s, %s, %s)
    """, (name, email, password, role))
    
    user_id = cursor.lastrowid
    print(f"✅ User created with ID: {user_id}")
    print(f"   Name: {name}")
    print(f"   Email: {email}")
    print(f"   Password: password123")
    
    # Now add sample forum posts with this user
    print("\n📝 Adding sample forum posts...")
    
    cursor.execute("""
        INSERT INTO forum_posts (user_id, title, body) VALUES
        (%s, 'Welcome to the PetCheck Forum!', 'This is a place where pet owners can share experiences and ask questions. Feel free to introduce yourself and your furry friends!'),
        (%s, 'My dog has a skin rash - what should I do?', 'I noticed my dog scratching a lot and saw red patches on his belly. Has anyone experienced this before?'),
        (%s, 'Best food for puppies in Uganda?', 'I just got a new puppy. What local foods are safe and healthy for him?')
    """, (user_id, user_id, user_id))
    
    print("✅ 3 sample forum posts added")
    
    # Add sample replies
    cursor.execute("SELECT id FROM forum_posts LIMIT 1")
    post_id = cursor.fetchone()[0]
    
    cursor.execute("""
        INSERT INTO forum_replies (post_id, user_id, body) VALUES
        (%s, %s, 'Welcome! Feel free to ask any questions about your pets.')
    """, (post_id, user_id))
    
    print("✅ Sample reply added")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("=" * 50)
    print("✅ ALL DONE!")
    print("=" * 50)
    print("\n🔐 Login credentials:")
    print("   Email: demo@petcheck.com")
    print("   Password: password123")
    print("\n🎯 Next: Run python app.py")
    
except Exception as e:
    print(f"❌ Error: {e}")