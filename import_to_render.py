import psycopg2

# YOUR DATABASE URL
DATABASE_URL = "postgresql://petcheck_user:0AP1slR7LAcIJ20un8aKaFXVBmCYgjwy@dpg-d8m6s3a8qa3s73acp3qg-a.oregon-postgres.render.com:5432/petcheck_udn9"

print("🔌 Connecting to Render PostgreSQL...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
print("✅ Connected!")

print("📖 Reading SQL file...")
with open('petcheck_postgres_fixed.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

print("🚀 Executing SQL...")

# Execute each statement separately
statements = sql.split(';')
count = 0

for stmt in statements:
    stmt = stmt.strip()
    if stmt and len(stmt) > 5:
        try:
            cursor.execute(stmt)
            count += 1
            if count % 10 == 0:
                print(f"   Executed {count} statements...")
        except Exception as e:
            error = str(e)
            if 'already exists' not in error.lower() and 'duplicate' not in error.lower():
                print(f"   Warning: {error[:80]}")

conn.commit()
print(f"✅ Executed {count} statements!")

# Verify
print("\n📊 Verifying data:")
cursor.execute("SELECT COUNT(*) FROM vets")
print(f"   Vets: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM articles")
print(f"   Articles: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM users")
print(f"   Users: {cursor.fetchone()[0]}")

cursor.close()
conn.close()