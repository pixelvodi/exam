# import pyodbc
# import logging
#
# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8', force=True)
# logger = logging.getLogger(__name__)
#
# DB_CONFIG = {
#     "driver": "{ODBC Driver 17 for SQL Server}",
#     "server": "localhost,1433",
#     "database": "demoappSQL",
#     "uid": "sa",
#     "pwd": "YourStrongPassword123!",
#     "ConnectionTimeout": 5
# }
#
# def get_connection():
#     try:
#         conn = pyodbc.connect(f"Driver={DB_CONFIG['driver']};Server={DB_CONFIG['server']};Database={DB_CONFIG['database']};UID={DB_CONFIG['uid']};PWD={DB_CONFIG['pwd']};Encrypt=yes;TrustServerCertificate=yes;")
#         return conn
#     except Exception as e:
#         logger.error(f"Ошибка подключения: {e}")
#         return None
#
# def _exec(query, params=(), fetch=True, commit=False):
#     conn = get_connection()
#     if not conn: return None if fetch else False
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute(query, params)
#             if cursor.description:
#                 cols = [c[0] for c in cursor.description]
#                 res = cursor.fetchone() if fetch else cursor.fetchall()
#                 return dict(zip(cols, res)) if fetch else ([dict(zip(cols, r)) for r in res] if res else [])
#             if commit: conn.commit()
#             return None if fetch else True
#     except Exception as e:
#         logger.error(f"Query error: {e}")
#         return None if fetch else False
#     finally:
#         conn.close()
#
# def get_role_id(name): return _exec("SELECT id FROM roles WHERE LOWER(role_name)=LOWER(?)", (name,))['id']
#
# def add_user(username, email, role_name, password):
#     role_id = get_role_id(role_name)
#     if not role_id: return False, f"Роль '{role_name}' не найдена."
#     try:
#         _exec("INSERT INTO users (username, email, role_id, password) VALUES (?, ?, ?, ?)", (username, email, role_id, password), commit=True)
#         return True, "Пользователь зарегистрирован!"
#     except Exception as e: return False, str(e)
#
# check_email_exists = lambda e: _exec("SELECT id FROM users WHERE email=?", (e,)) is not None
#
# def login_user(email, password):
#     user = _exec("SELECT u.username, r.role_name FROM users u JOIN roles r ON u.role_id=r.id WHERE u.email=? AND u.password=?", (email, password))
#     return (True, user) if user else (False, "Неверный пароль или почта")
#
# def get_products(search="", sort=""):
#     sql, params = "SELECT id, name, price, stock_quantity, description, image_url, size FROM products WHERE 1=1", []
#     if search: sql, params = sql + " AND name LIKE ?", params + [f"%{search}%"]
#     if sort == "Цена ↑": sql += " ORDER BY price ASC"
#     elif sort == "Цена ↓": sql += " ORDER BY price DESC"
#     return _exec(sql, params, fetch=False) or []
#
# get_all_products = lambda: _exec("SELECT * FROM products", fetch=False) or []
# get_all_brands = lambda: _exec("SELECT id, name FROM brands", fetch=False) or []
# get_all_colors = lambda: _exec("SELECT id, name FROM colors", fetch=False) or []
#
# def delete_product(pid): _exec("DELETE FROM products WHERE id=?", (pid,), commit=True)
#
# def add_product(name, price, stock, desc, img, brand_id=None, color_id=None, size=None):
#     try:
#         _exec("INSERT INTO products (name, price, stock_quantity, description, image_url, brand_id, color_id, size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, price, stock, desc, img, brand_id, color_id, size), commit=True)
#         return True, "Товар добавлен"
#     except Exception as e: return False, str(e)
#
# get_brand_id_by_name = lambda n: _exec("SELECT id FROM brands WHERE name=?", (n,))['id']
# get_color_id_by_name = lambda n: _exec("SELECT id FROM colors WHERE name=?", (n,))['id']
# get_product_by_id = lambda pid: _exec("SELECT id, name, price, stock_quantity, description, image_url, brand_id, color_id, size FROM products WHERE id=?", (pid,))
#
# def update_product_full(pid, name, price, desc=None, img=None, brand_id=None, color_id=None, size=None, stock=None):
#     try:
#         _exec("UPDATE products SET name=?, price=?, description=?, image_url=?, brand_id=?, color_id=?, size=?, stock_quantity=? WHERE id=?", (name, price, desc, img, brand_id, color_id, size, stock, pid), commit=True)
#         return True
#     except Exception as e: return False
#
# get_all_orders = lambda: _exec("SELECT o.id, o.user_id, o.order_date, o.status, o.total, u.username FROM orders o LEFT JOIN users u ON o.user_id=u.id ORDER BY o.order_date DESC", fetch=False) or []
# get_order_items = lambda oid: _exec("SELECT p.name, oi.quantity, oi.price FROM order_items oi JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?", (oid,), fetch=False) or []
#
# def delete_order(oid):
#     _exec("DELETE FROM order_items WHERE order_id=?", (oid,), commit=True)
#     _exec("DELETE FROM orders WHERE id=?", (oid,), commit=True)
#
# def create_order(user_id, items):
#     if not items: return False
#     try:
#         conn = get_connection()
#         with conn.cursor() as cursor:
#             cursor.execute("INSERT INTO orders (user_id, order_date, status, total) VALUES (?, GETDATE(), 'Новый', 0)", (user_id,))
#             oid = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]
#             total = 0
#             for item in items:
#                 p = get_product_by_id(item['product_id'])
#                 if p:
#                     cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?,?,?,?)", (oid, item['product_id'], item['quantity'], p['price']))
#                     total += p['price'] * item['quantity']
#             cursor.execute("UPDATE orders SET total=? WHERE id=?", (total, oid))
#             conn.commit()
#         return True
#     except Exception as e:
#         print("Ошибка:", e)
#         return False
#
# get_product_by_name = lambda n: _exec("SELECT id, price, name FROM products WHERE name=?", (n,))
# get_user_by_username = lambda u: _exec("SELECT id, username FROM users WHERE username=?", (u,))
# get_brand_name_by_id = lambda bid: _exec("SELECT name FROM brands WHERE id=?", (bid,))['name'] or ""
# get_color_name_by_id = lambda cid: _exec("SELECT name FROM colors WHERE id=?", (cid,))['name'] or ""
# get_order_by_id = lambda oid: _exec("SELECT * FROM orders WHERE id=?", (oid,))
#
# def update_order_status(oid, status):
#     try:
#         _exec("UPDATE orders SET status=? WHERE id=?", (status, oid), commit=True)
#         return True
#     except Exception as e:
#         logger.error(f"Ошибка: {e}")
#         return False


import pyodbc
import logging

DB_CONFIG = {
    "driver": "{ODBC DRIVER 17 for SQL Server}",
    "server": "localhost,1433",
    "database": "demoappSQL",
    "uid": "sa",
    "pwd": "YourStrongPassword123!",
    "ConnectionTimeout": 5
}

def get_connection():
    try:
        conn = pyodbc.connect(f"Driver={DB_CONFIG['driver']};Server={DB_CONFIG['server']};Database={DB_CONFIG['database']};UID={DB_CONFIG['uid']};PWD={DB_CONFIG['pwd']};Encrypt=yes;TrustServerCertificate=yes;")
        return conn
    except Exception as e:
        return None

def _exec(query, params=(), fetch=True, commit=False):
    conn = get_connection()
    if not conn: return None if fetch else False
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                cols = [c[0] for c in cursor.description]
                res = cursor.fetchone() if fetch else cursor.fetchall()
                return dict(zip(cols, res)) if fetch else ([dict(zip(cols, r)) for r in res] if res else [])
            if commit: conn.commit()
            return None if fetch else True
    except Exception as e:
        return None if fetch else False
    finally:
        conn.close()

def get_role_id(name): return _exec("SELECT id FROM roles WHERE LOWER(role_name)=LOWER(?)", (name,))['id']

def add_user(username, email, role_name, password):
    role_id = get_role_id(role_name)
    if not role_id: return False, f"Роль {role_name} не найдена"
    try:
        _exec("INSERT INTO users (username, email, role_id, password) VALUES (?, ?, ?, ?)", (username, email, role_id, password), commit=True)
        return True, "Пользователь зареган"
    except Exception as e:
        return False, str(e)

check_email_exists = lambda e: _exec("SELECT id FROM users WHERE email=?", (e,)) is not None

def login_user(email, password):
    user = _exec("SELECT u.username, r.role_name FROM user u JOIN roles r ON u.role_id = r.id WHERE u.email=? AND u.password=?", (email, password))
    return (True, user) if user else (False, "Неверный пароль или почта")

def get_products(search="", sort=""):
    sql, params = "SELECT id, name, price, stock_quantity, description, image_url, size FROM products WHERE 1=1", []
    if search: sql, params = sql + "AND name LIKE ?", params + [f"%{search}%"]
    if sort == "Цена выше": sql += " ORDER BY price ASC"
    elif sort == "Цена ниже": sql += " ORDER BY price DESC"
    return _exec(sql, params, fetch=False) or []

get_all_products = lambda: _exec("SELECT * FROM products", fetch=False) or []
get_all_brands = lambda: _exec("SELECT * FROM brands", fetch=False) or []
get_all_colors = lambda: _exec("SELECT * FROM colors", fetch=False) or []

def delete_product(pid): _exec("DELETE FROM products WHERE id=?", (pid,), commit=True)

def add_product(name, price, stock, desc, img, brand_id=None, color_id=None, size=None):
    try:
        _exec("INSERT INTO products (name, price, stock_quantity, description, image_url, brand_id, color_id, size) VALUES (?,?,?,?,?,?,?,?)", (name, price, stock, desc, img, brand_id, color_id, size), commit=True)
        return True, "ТОвар добавлен"
    except Exception as e: return False, str(e)

get_brand_id_by_name = lambda n: _exec("SELECT id FROM brands WHERE name=?", (n,))['id']
get_color_id_by_name = lambda n: _exec("SELECT id FROM colors WHERE name=?", (n,))['id']
get_product_by_id = lambda pid: _exec("SELECT id, name, price, stock_quantity, description, image_url, brand_id, color_id, size FROM products WHERE id=?", (pid,))

def update_product_full(pid, name, price, desc=None, img=None, brand_id=None, color_id=None, size=None, stock=None):
    try:
        _exec("UPDATE products SET name=?, price=?, description=?, image_url=?, brand_id=?, color_id=?, stock_qantity=? WHERE id=?", (name, price, desc, img, brand_id, color_id, size, stock, pid), commit=True)
        return True
    except Exception as e: return False

get_all_orders = lambda: _exec("SELECT o.id, o.user_id, o.order_date, o.status, o.total, u.username, FROM orders o LEFT JOIN users u ON o.user_id=u.id ORDER BY o.order_date DESC", fetch=False) or []
get_order_items = lambda oid: _exec("SELECT p.name, oi.quantity, oi.price FROM order_items oi JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?", (oid,), fetch=False) or []

def delete_order(oid):
    _exec("DELETE FROM order_items WHERE order_id=?", (oid,), commit=True)
    _exec("DELETE FROM orders WHERE id=?", (oid,), commit=True)

def create_order(user_id, items):
    if not items: return False
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO orders (user_id, order_date, status, total) VALUES (?, GETDATE(), 'Новый', 0)", (user_id,))
            oid = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]
            total = 0
            for item in items:
                p = get_product_by_id(item['product_id'])
                if p:
                    cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?,?,?,?)", (oid, item['product_id'], item['quantity'], p['price']))
                    total += p['price'] * item['quantity']
            cursor.execute("UPDATE orders SET total=? WHERE id=?", (total, oid))
            conn.commit()
        return True
    except Exception as e:
        return False

get_product_by_name = lambda n: _exec("SELECT id, price, name FROM products WHERE name=?", (n,))
get_user_by_username = lambda u: _exec("SELECT id, username FROM users WHERE username=?", (u,))
get_brand_name_by_id = lambda bid: _exec("SELECT name FROM brands WHERE id=?", (bid,))['name'] or ""
get_color_name_by_id = lambda cid: _exec("SELECT name FROM color WHERE id", (cid,))['name'] or ""
get_order_by_id = lambda oid: _exec("SELECT * FROM orders WHERE id=?", (oid,))

def update_order_status(oid, status):
    try:
        _exec("UPDATE orders SET status=? WHERE id=?", (status, oid), commit=True)
        return True
    except Exception as e:
        return False