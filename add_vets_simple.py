import psycopg2

# Your Render PostgreSQL connection details
conn = psycopg2.connect(
    host="dpg-d8m6s3a8qa3s73acp3qg-a.oregon-postgres.render.com",
    port=5432,
    database="petcheck_udn9",
    user="petcheck_user",
    password="0AP1slR7LAcIJ20un8aKaFXVBmCYgjwy"
)

cursor = conn.cursor()
print("✅ Connected to database!")

# Vets to add
vets = [
    ('Dr. Aisha Nambi', 'Divine Pet Clinic', '+256701234567', 'aisha.nambi@divinepet.ug', 'Division A, Entebbe', 'Dermatology & Surgery', True),
    ('Dr. John Kayongo', 'Entebbe Pet Hospital', '+256789123456', 'john.kayongo@epthospital.ug', 'Division B, Entebbe', 'Emergency & Critical Care', True),
    ('Dr. Grace Atim', 'Happy Pets Vet', '+256703456789', 'grace.atim@happypets.ug', 'Division A, Entebbe', 'Dentistry & Nutrition', True),
]

print("\n📝 Adding vets...")
for vet in vets:
    try:
        cursor.execute("""
            INSERT INTO vets (name, clinic_name, phone, email, location, specialization, available) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, vet)
        print(f"   ✅ Added: {vet[0]}")
    except Exception as e:
        if 'duplicate' in str(e).lower():
            print(f"   ⚠️ Already exists: {vet[0]}")
        else:
            print(f"   ❌ Error: {e}")

conn.commit()
print("\n✅ Done!")

# Show all vets
cursor.execute("SELECT id, name, specialization FROM vets")
print("\n📋 All vets in database:")
for vet in cursor.fetchall():
    print(f"   {vet[0]}. {vet[1]} - {vet[2]}")

cursor.close()
conn.close()