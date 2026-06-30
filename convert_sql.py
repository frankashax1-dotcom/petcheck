import re

print("📁 Reading MySQL backup...")
with open('petcheck_backup.sql', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("🔄 Converting to PostgreSQL format...")

# Remove comments and empty lines
lines = content.split('\n')
cleaned_lines = []
for line in lines:
    line = line.strip()
    if line and not line.startswith('--'):
        cleaned_lines.append(line)

content = '\n'.join(cleaned_lines)

# Replace MySQL syntax with PostgreSQL
content = re.sub(r'`', '"', content)
content = re.sub(r'AUTO_INCREMENT', 'SERIAL', content)
content = re.sub(r'UNSIGNED', '', content)
content = re.sub(r'ENGINE=InnoDB', '', content)
content = re.sub(r'CHARSET=\w+', '', content)
content = re.sub(r'COLLATE=\w+', '', content)
content = re.sub(r"\\'", "''", content)
content = re.sub(r'0000-00-00 00:00:00', '1970-01-01 00:00:00', content)
content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)

# Remove MySQL specific lines
lines = content.split('\n')
filtered_lines = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    skip_keywords = ['SET SQL_MODE', 'SET FOREIGN_KEY_CHECKS', 'CREATE DATABASE', 
                     'USE ', 'DEFAULT CHARSET', 'COLLATE', 'SET @', 'GTID', 
                     'LOCK TABLES', 'UNLOCK TABLES']
    skip = False
    for keyword in skip_keywords:
        if keyword in line:
            skip = True
            break
    if not skip:
        filtered_lines.append(line)

content = '\n'.join(filtered_lines)

# Fix specific issues
content = re.sub(r'\(-1,', '(-1,', content)
content = re.sub(r'\)\s*;', ');', content)

# Save converted file
with open('petcheck_postgres_fixed.sql', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Conversion complete!")
print("   File saved as: petcheck_postgres_fixed.sql")
print(f"   Original size: {len(content)} characters")