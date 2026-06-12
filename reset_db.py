import pymysql

# YOUR MYSQL PASSWORD
MYSQL_PASSWORD = "2026"

print("=" * 50)
print("🔄 Resetting PetCheck Database...")
print("=" * 50)

# Read schema file
try:
    with open('schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
    print("✅ schema.sql loaded")
except FileNotFoundError:
    print("❌ schema.sql not found! Make sure it's in the same folder")
    exit(1)

# Connect to MySQL
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password=MYSQL_PASSWORD,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    print("✅ Connected to MySQL")
    
    # Drop and recreate database
    print("🗑️  Dropping old database...")
    cursor.execute("DROP DATABASE IF EXISTS petcheck")
    
    print("📦 Creating new database...")
    cursor.execute("CREATE DATABASE petcheck")
    cursor.execute("USE petcheck")
    
    # Execute schema
    print("📝 Running schema.sql...")
    statements = schema.split(';')
    count = 0
    for statement in statements:
        if statement.strip():
            try:
                cursor.execute(statement)
                count += 1
            except Exception as e:
                print(f"   ⚠️  Warning: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("=" * 50)
    print(f"✅ SUCCESS! {count} statements executed")
    print("=" * 50)
    print("\n🎯 Next steps:")
    print("   1. Run: python app.py")
    print("   2. Visit: http://127.0.0.1:5000")
    
except pymysql.Error as e:
    print(f"\n❌ MySQL Error: {e}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")