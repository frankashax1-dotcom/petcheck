import pymysql

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='2026',
    database='petcheck',
    charset='utf8mb4'
)

cursor = conn.cursor()

# Clear existing vets
cursor.execute("DELETE FROM vets")

# Add vet data
vets = [
    ('Dr. Ssali James', 'Entebbe Veterinary Clinic', '+256700123456', 'james.ssali@vetclinic.ug', 'Division A, Entebbe', 'Dogs & Cats', 1),
    ('Dr. Nakato Sarah', 'PetCare Entebbe', '+256782654321', 'sarah.nakato@petcare.ug', 'Division B, Entebbe', 'Small Animals', 1),
    ('Dr. Mukasa David', 'Animal Health Center', '+256755987654', 'david.mukasa@animalhealth.ug', 'Kampala Rd, Entebbe', 'General Veterinary', 1),
    ('Dr. Aisha Nambi', 'Divine Pet Clinic', '+256701234567', 'aisha.nambi@divinepet.ug', 'Division A, Entebbe', 'Dermatology & Surgery', 1),
    ('Dr. John Kayongo', 'Entebbe Pet Hospital', '+256789123456', 'john.kayongo@epthospital.ug', 'Division B, Entebbe', 'Emergency & Critical Care', 1),
    ('Dr. Grace Atim', 'Happy Pets Vet', '+256703456789', 'grace.atim@happypets.ug', 'Division A, Entebbe', 'Dentistry & Nutrition', 1)
]

cursor.executemany("""
    INSERT INTO vets (name, clinic_name, phone, email, location, specialization, available) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", vets)

conn.commit()
print(f"✅ Added {len(vets)} vets to database!")

# Verify
cursor.execute("SELECT COUNT(*) FROM vets")
count = cursor.fetchone()[0]
print(f"📊 Total vets in database: {count}")

cursor.close()
conn.close()