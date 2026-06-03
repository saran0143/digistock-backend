import sqlite3

def init_db():
    # Connects to your unified core database file
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()

    # Enforce foreign key constraints so cascading deletes work perfectly
    conn.execute("PRAGMA foreign_keys = ON;")

    print("Creating database tables...")

    # 1. Categories table
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 2. Brands table
    c.execute('''CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
    )''')

    # 3. Inventory table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        brand_id INTEGER NOT NULL,
        model TEXT NOT NULL,
        price INTEGER NOT NULL,
        stock INTEGER NOT NULL,
        ram TEXT,
        storage TEXT,
        processor TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
        FOREIGN KEY (brand_id) REFERENCES brands (id) ON DELETE CASCADE
    )''')

    print("Seeding default application data...")

    # Seed Default Categories
    categories = ['Mobiles', 'Accessories', 'Refrigerator', 'TV', 'Air Conditioner', 'Home Theater', 'Laptops']
    for cat in categories:
        c.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat,))

    # Seed Default Brands dynamically linked to the 'Mobiles' category ID
    c.execute('SELECT id FROM categories WHERE name=?', ('Mobiles',))
    row = c.fetchone()
    if row:
        mobile_id = row[0]
        mobile_brands = ['Samsung', 'Apple', 'Xiaomi', 'OnePlus', 'Realme', 'Vivo', 'Oppo', 'Nothing']
        for brand in mobile_brands:
            c.execute('INSERT OR IGNORE INTO brands (name, category_id) VALUES (?,?)', (brand, mobile_id))

    conn.commit()
    conn.close()
    print("Database completely built and seeded successfully! ✅")

if __name__ == "__main__":
    init_db()