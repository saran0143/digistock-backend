from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import datetime
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "DigiStock Backend Running 🔥", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app = FastAPI()

# CORS - React frontend connect avvadaniki
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost",
        "http://127.0.0.1:3000",
        "http://127.0.0.1",
        "http://192.168.29.50:3000"
        "http://127.0.0.1:55752"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LoginRequest(BaseModel):
    username: str
    password: str
    role: str

class CategoryCreate(BaseModel):
    name: str

class BrandCreate(BaseModel):
    name: str
    category_id: int

class BrandUpdate(BaseModel):
    name: str

class InventoryCreate(BaseModel):
    model: str
    price: int
    stock: int
    ram: Optional[str] = None
    storage: Optional[str] = None
    processor: Optional[str] = None

class InventoryUpdate(BaseModel):
    model: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    processor: Optional[str] = None

class StockUpdate(BaseModel):
    stock: int

# Helper function
def check_permission(role: str, action: str):
    if action == 'read':
        return True
    if action == 'stock_update' and role in ['staff', 'manager', 'admin']:
        return True
    if action in ['create', 'update', 'delete'] and role in ['admin', 'manager']:
        return True
    return False

# ========== LIVE STATS ANALYTICS ==========
@app.get("/api/stats")
def get_dashboard_stats():
    """Calculates summary cards dynamically for Manager and Staff dashboards."""
    try:
        conn = sqlite3.connect('inventory.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Calculate dynamic totals
        c.execute("SELECT COUNT(*) as total_prod, SUM(price * stock) as total_val FROM inventory")
        res = c.fetchone()
        
        # Calculate low stock threshold count (< 5 items)
        c.execute("SELECT COUNT(*) as low_count FROM inventory WHERE stock < 5")
        low_res = c.fetchone()
        
        conn.close()
        
        total_products = res["total_prod"] or 0
        raw_value = res["total_val"] or 0
        low_stock = low_res["low_count"] or 0
        
        # Turn raw pricing numbers into clean string badges (e.g., Lakhs)
        if raw_value >= 100000:
            total_value = f"₹{(raw_value / 100000):.1f}L"
        else:
            total_value = f"₹{(raw_value / 1000):.1f}K" if raw_value > 0 else "₹0"
            
        return {
            "totalProducts": total_products,
            "lowStock": low_stock,
            "totalValue": total_value,
            "todaySales": "₹45.2K"  # Consistent mockup tracker metric placeholder
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== LOGIN ==========
@app.post("/api/login")
def login(data: LoginRequest):
    users = {
        "admin": {"password": "admin123", "role": "admin"},
        "manager": {"password": "manager123", "role": "manager"},
        "staff": {"password": "staff123", "role": "staff"}
    }

    user = users.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if user["role"] != data.role:
        raise HTTPException(status_code=401, detail="Role mismatch")

    return {
        "username": data.username,
        "role": user["role"]
    }

# ========== CATEGORIES ==========
@app.get("/api/categories")
def get_categories():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT c.id, c.name, COUNT(DISTINCT b.id) as brandCount
                 FROM categories c
                 LEFT JOIN brands b ON c.id = b.category_id
                 GROUP BY c.id, c.name''')
    categories = [{"id": row[0], "name": row[1], "brandCount": row[2]} for row in c.fetchall()]
    conn.close()
    return categories

@app.post("/api/categories")
def create_category(data: CategoryCreate, role: str = Query(...)):
    if not check_permission(role, 'create'):
        raise HTTPException(status_code=403, detail="Permission denied")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO categories (name) VALUES (?)', (data.name,))
        conn.commit()
        cat_id = c.lastrowid
        conn.close()
        return {"id": cat_id, "name": data.name, "brandCount": 0}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Category already exists")

@app.put("/api/categories/{category_id}")
def update_category(category_id: int, data: CategoryCreate, role: str = Query(...)):
    if not check_permission(role, 'update'):
        raise HTTPException(status_code=403, detail="Permission denied")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('UPDATE categories SET name=? WHERE id=?', (data.name, category_id))
    conn.commit()
    conn.close()
    return {"id": category_id, "name": data.name}

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, role: str = Query(...)):
    if not check_permission(role, 'delete'):
        raise HTTPException(status_code=403, detail="Permission denied")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('DELETE FROM categories WHERE id=?', (category_id,))
    conn.commit()
    conn.close()
    return {"message": "Category deleted"}

# ========== BRANDS ==========
@app.get("/api/brands/{category_id}")
def get_brands(category_id: int):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT b.id, b.name, COUNT(i.id) as productCount
                 FROM brands b
                 LEFT JOIN inventory i ON b.id = i.brand_id
                 WHERE b.category_id=?
                 GROUP BY b.id, b.name''', (category_id,))
    brands = [{"id": row[0], "name": row[1], "productCount": row[2]} for row in c.fetchall()]
    conn.close()
    return brands

@app.post("/api/brands")
def create_brand(data: BrandCreate, role: str = Query(...)):
    if not check_permission(role, 'create'):
        raise HTTPException(status_code=403, detail="Permission denied")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('INSERT INTO brands (name, category_id) VALUES (?,?)', (data.name, data.category_id))
    conn.commit()
    brand_id = c.lastrowid
    conn.close()
    return {"id": brand_id, "name": data.name, "category_id": data.category_id, "productCount": 0}

@app.put("/api/brands/{brand_id}")
def update_brand(brand_id: int, data: BrandUpdate, role: str = Query(...)):
    if not check_permission(role, 'update'):
        raise HTTPException(status_code=403, detail="Permission denied")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('UPDATE brands SET name=? WHERE id=?', (data.name, brand_id))
    conn.commit()
    conn.close()
    return {"id": brand_id, "name": data.name}

@app.delete("/api/brands/{brand_id}")
def delete_brand(brand_id: int, role: str = Query(...)):
    if not check_permission(role, 'delete'):
        raise HTTPException(status_code=403, detail="Permission denied")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('DELETE FROM brands WHERE id=?', (brand_id,))
    conn.commit()
    conn.close()
    return {"message": "Brand deleted"}

# ========== INVENTORY ==========
@app.get("/api/inventory/{category_id}/{brand_id}")
def get_inventory(category_id: int, brand_id: int):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''SELECT id, model, price, stock, ram, storage, processor
                 FROM inventory
                 WHERE category_id=? AND brand_id=?''', (category_id, brand_id))
    products = []
    for row in c.fetchall():
        products.append({
            "id": row[0],
            "model": row[1],
            "price": row[2],
            "stock": row[3],
            "ram": row[4],
            "storage": row[5],
            "processor": row[6]
        })
    conn.close()
    return products

@app.post("/api/inventory/{category_id}/{brand_id}")
def create_product(category_id: int, brand_id: int, data: InventoryCreate, role: str = Query(...)):
    if not check_permission(role, 'create'):
        raise HTTPException(status_code=403, detail="Permission denied - Only Admin/Manager can add products")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''INSERT INTO inventory (category_id, brand_id, model, price, stock, ram, storage, processor)
                 VALUES (?,?,?,?,?,?,?,?)''',
              (category_id, brand_id, data.model, data.price, data.stock, data.ram, data.storage, data.processor))
    conn.commit()
    product_id = c.lastrowid
    conn.close()
    return {"id": product_id, **data.dict()}

@app.put("/api/inventory/{product_id}")
def update_product(product_id: int, data: InventoryUpdate, role: str = Query(...)):
    if not check_permission(role, 'update'):
        raise HTTPException(status_code=403, detail="Permission denied - Only Admin/Manager can update")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()

    # Build dynamic update query
    fields = []
    values = []
    for field, value in data.dict(exclude_unset=True).items():
        if value is not None:
            fields.append(f"{field}=?")
            values.append(value)

    if fields:
        values.append(product_id)
        query = f"UPDATE inventory SET {', '.join(fields)} WHERE id=?"
        c.execute(query, values)
        conn.commit()

    conn.close()
    return {"message": "Product updated"}

@app.put("/api/inventory/{product_id}/stock")
def update_stock(product_id: int, data: StockUpdate, role: str = Query(...)):
    if not check_permission(role, 'stock_update'):
        raise HTTPException(status_code=403, detail="Permission denied")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('UPDATE inventory SET stock=? WHERE id=?', (data.stock, product_id))
    conn.commit()
    conn.close()
    return {"message": "Stock updated"}

@app.delete("/api/inventory/{product_id}")
def delete_product(product_id: int, role: str = Query(...)):
    if not check_permission(role, 'delete'):
        raise HTTPException(status_code=403, detail="Permission denied - Only Admin/Manager can delete")

    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('DELETE FROM inventory WHERE id=?', (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Product deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
