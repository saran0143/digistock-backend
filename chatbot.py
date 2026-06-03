from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import re

app = Flask(__name__)
CORS(app)

def get_db():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_all_brands_from_db():
    """Dynamically fetches all active brand names from the DB to match user input."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT lower(name) as brand_name FROM brands")
        brands = [row["brand_name"] for row in cur.fetchall()]
        conn.close()
        return brands
    except Exception:
        return []

@app.route('/')
def home():
    return "DigiStock NLP Chatbot Engine Running on Port 5001!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "").strip().lower()

    if not message:
        return jsonify({"reply": "I didn't catch that. Could you please rephrase?"})

    conn = get_db()
    cur = conn.cursor()

    # ==========================================
    # INTENT 1: Total Products / Inventory Count
    # Matches: "total products", "how many items", "stock count", "inventory size"
    # ==========================================
    if re.search(r'(total|how many|count|size|all).*product', message) or "inventory" in message:
        cur.execute("SELECT COUNT(*) as count FROM inventory")
        count = cur.fetchone()["count"]
        conn.close()
        return jsonify({"reply": f"📊 There are currently {count} total product items tracked in the DigiStock system."})

    # ==========================================
    # INTENT 2: Low Stock Warning Audit
    # Matches: "low stock", "running out", "alert", "depleted", "minimum stock"
    # ==========================================
    elif "low stock" in message or "running out" in message or "alert" in message:
        cur.execute("SELECT model, stock FROM inventory WHERE stock < 5")
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return jsonify({"reply": "✅ Exceptional inventory status! No low stock thresholds (less than 5 units) have been tripped."})

        text = "⚠️ **Low Stock Alert (Less than 5 units left):**\n"
        for row in rows:
            text += f"• {row['model']} — **{row['stock']} units left**\n"
        return jsonify({"reply": text})

    # ==========================================
    # INTENT 3: Dynamic Brand Query Extraction
    # Automatically extracts and searches ANY brand name stored in your database
    # ==========================================
    else:
        known_brands = get_all_brands_from_db()
        matched_brand = None

        # Check if any database brand name exists inside the user's string message
        for brand in known_brands:
            if re.search(rf'\b{brand}\b', message):
                matched_brand = brand
                break

        if matched_brand:
            cur.execute("""
                SELECT i.model, i.price, i.stock
                FROM inventory i
                JOIN brands b ON i.brand_id = b.id
                WHERE lower(b.name) = ?
            """, (matched_brand,))
            rows = cur.fetchall()
            conn.close()

            if not rows:
                return jsonify({"reply": f"🔍 I found the brand '{matched_brand.upper()}' in our registry, but there are no product models in stock for it right now."})

            text = f"📱 **Current {matched_brand.upper()} Catalog:**\n"
            for row in rows:
                text += f"• {row['model']} | Price: ₹{row['price']:,} | Stock: {row['stock']} units\n"
            return jsonify({"reply": text})

    # ==========================================
    # FALLBACK LAYER: Helpful Interactive Guide
    # ==========================================
    conn.close()
    return jsonify({
        "reply": (
            "🤖 **DigiStock AI Helper**: I didn't quite understand that phrase. "
            "Try asking me conversational questions like:\n\n"
            "💡 *'How many total products do we have right now?'*\n"
            "💡 *'Are there any low stock warnings I should check?'*\n"
            "💡 *'Show me what items we have for Samsung or Apple'* (or any brand in your store!)"
        )
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)