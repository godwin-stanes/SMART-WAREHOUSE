from flask import Flask, request, jsonify, render_template
import sqlite3



app = Flask(__name__)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    rfid TEXT,
                    quantity INTEGER DEFAULT 1
                )""")
    conn.commit()
    conn.close()

def dict_factory(cursor, row):
    """Helper: convert rows to dictionary instead of tuple"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@app.route("/")
def home():
    return render_template("index.html")

# --- Add item(s) ---
@app.route("/add_item", methods=["POST"])
def add_item():
    data = request.get_json()

    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()

    # If data is a single object → wrap it into a list
    if isinstance(data, dict):
        data = [data]

    for item in data:
        name, rfid = item["name"], item["rfid"]
        quantity = item.get("quantity", 1)  # Default = 1
        cur.execute("INSERT INTO items (name, rfid, quantity) VALUES (?, ?, ?)", 
                    (name, rfid, quantity))

    conn.commit()
    conn.close()
    return jsonify({"message": f"{len(data)} item(s) added successfully"})

# --- View items ---
@app.route("/items", methods=["GET"])
def get_items():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = dict_factory  # makes rows → dicts
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)

# --- Update item quantity ---
@app.route("/update_item/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()
    quantity = data.get("quantity")
    
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("UPDATE items SET quantity=? WHERE id=?", (quantity, item_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": f"Item {item_id} updated successfully"})

# --- Delete item ---
@app.route("/delete_item/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": f"Item {item_id} deleted successfully"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

@app.route("/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Item deleted successfully!"})

@app.route("/dashboard_data")
def dashboard_data():
    items = Item.query.all()
    data = {
        "stock": [{"name": i.name, "quantity": i.quantity} for i in items],
        "low_stock": sorted(
            [{"name": i.name, "quantity": i.quantity} for i in items],
            key=lambda x: x["quantity"]
        )[:5],
        "weekly_movement": [
            {"day": "Mon", "moved": 10},
            {"day": "Tue", "moved": 7},
            {"day": "Wed", "moved": 12},
            {"day": "Thu", "moved": 5},
            {"day": "Fri", "moved": 9},
            {"day": "Sat", "moved": 6},
            {"day": "Sun", "moved": 8},
        ]
    }
    return jsonify(data)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
