import pyodbc

DB_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "localhost,1433",
    "database": "demoappSQL",
    "uid": "sa",
    "pwd": "YourStrongPassword123!",
    "ConnectionTimeout": 5
}

def get_connection():
    try:
        return pyodbc.connect(
            f"Driver={DB_CONFIG['driver']};Server={DB_CONFIG['server']};"
            f"Database={DB_CONFIG['database']};UID={DB_CONFIG['uid']};"
            f"PWD={DB_CONFIG['pwd']};Encrypt=yes;TrustServerCertificate=yes;"
        )
    except Exception as e:
        return None

def _exec(query, params=(), fetch=True, commit=False):
    conn = get_connection()
    if not conn:
        return None if fetch else False
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                cols = [c[0] for c in cursor.description]
                res = cursor.fetchone() if fetch else cursor.fetchall()
                if fetch:
                    return dict(zip(cols, res)) if res else None
                return [dict(zip(cols, r)) for r in res] if res else []
            if commit:
                conn.commit()
            return None if fetch else True
    except Exception:
        return  None if fetch else None
    finally:
        conn.close()

def get_role_id(name):
    result = _exec("SELECT id FROM roles WHERE LOWER(role_name) = LOWER(?)", (name,))
    return result['id'] if result else None

def add_user(username, email, role_name, password):
    role_id = get_role_id(role_name)
    if not role_id:
        return False, f"Роль {role_name} не найдена"
    try:
        _exec(
            "INSERT INTO users (username, email, role_id, password) VALUES (?, ?, ?, ?)",
            (username, email, role_id, password),
            commit=True
        )
        return True, "Пользователь зарегистрирован"
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    user = _exec(
        "SELECT u.username, r.role_name FROM users u "
        "JOIN roles r ON u.role_id = r.id WHERE u.email = ? AND u.password = ?",
        (email, password)
    )
    return (True, user) if user else (False, "Неверный пароль или почта")

def get_products(search="", sort=""):
    sql = "SELECT id, name, price, stock_quantity, description, image_url, size FROM products WHERE 1=1"
    params=[]
    if search:
        sql += " AND name LIKE ?"
        params.append(f"%{search}%")
    if sort == "Цена выше":
        sql += " ORDER BY price ASC"
    elif sort == "Цена ниже":
        sql += " ORDER BY price DESC"
    return _exec(sql, params, fetch=False) or []

def get_all_products():
    return _exec("SELECT * FROM products", fetch=False) or []

def get_all_brands():
    return _exec("SELECT * FROM brands", fetch=False) or []

def get_all_colors():
    return _exec("SELECT * FROM colors", fetch=False) or []

def get_product_by_id(pid):
    return _exec(
        "SELECT id, name, price, stock_quantity, description, image_url, brand_id, color_id, size "
        "FROM products WHERE id = ?",
        (pid,)
    )

def get_product_by_name(name):
    return _exec("SELECT id, price, name FROM products WHERE name = ?", (name,))

def delete_product(pid):
    _exec("DELETE FROM products WHERE id = ?", (pid,), commit=True)

def add_product(name, price, stock, desc, img, brand_id=None, color_id=None, size=None):
    try:
        _exec(
            "INSERT INTO products (name, price, stock_quantity, description, image_url, brand_id, color_id, size) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, price, stock, desc, img, brand_id, color_id, size),
            commit=True
        )
        return True, "Товар добавлен"
    except Exception as e:
        return False, str(e)

def update_product_full(pid, name, price, desc=None, img=None, brand_id=None, color_id=None, size=None, stock=None):
    try:
        _exec(
            "UPDATE products SET name=?, price=?, description=?, image_url=?, "
            "brand_id=?, color_id=?, size=?, stock_quantity=?, WHERE id=?",
            (name, price, desc, img, brand_id, color_id, size, stock, pid),
            commit=True
        )
        return True
    except Exception:
        return False

def get_all_orders():
    return _exec(
        "SELECT o.id, o.user_id, o.order_date, o.status, o.total, u.username "
        "FROM orders o LEFT JOIN users u ON o.user_if = u.id ORDER BY o.order_date DESC",
        fetch=False
    ) or []

def get_order_items(order_id):
    return _exec(
        "SELECT p.name, oi.quantity, oi.price, FROM order_items oi "
        "JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?",
        (order_id,),
        fetch=False
    ) or []

def delete_order(oid):
    _exec("DELETE FROM order_items WHERE order_id = ?", (oid,), commit=True)
    _exec("DELETE FROM orders WHERE id=?", (oid,), commit=True)

def create_order(user_id, items):
    if not items:
        return False
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO orders (user_id, order_date, status, total) VALUES(?, GETDATE(), 'Новый', 0)",
                (user_id,)
            )
            oid = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]
            total = 0
            for item in items:
                p = get_product_by_id(item['product_id'])
                if p:
                    cursor.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                        (oid, item['product_id'], item['quantity'], p['price'])
                    )
                    total += p['price'] * item['quantity']
            cursor.execute("UPDATE orders SET total = ? WHERE id = ?", (total, oid))
            conn.commit()
        return True
    except Exception:
        return False

def get_user_by_username(username):
    return _exec("SELECT id, username FROM users WHERE username = ?", (username,))

def update_order_status(oid, status):
    try:
        _exec("UPDATE orders SET status = ? WHERE id = ?", (status, oid), commit=True)
        return True
    except Exception:
        return False


# import pyodbc
# import socket
#
#
# def get_connection():
#     # Определяем, где мы находимся, по имени компьютера
#     computer_name = socket.gethostname().lower()
#
#     # Если имя компа домашнее (можешь вписать сюда имя своего ПК, если хочешь)
#     # Или просто проверяем через try/except, как в прошлый раз
#
#     print("Пробуем подключиться в режиме 'Колледж' (LocalDB)...")
#     try:
#         return pyodbc.connect(
#             f"Driver={{ODBC Driver 17 for SQL Server}};"
#             f"Server=(localdb)\\MSSQLLocalDB;"
#             f"Database=demoappSQL;"
#             f"Trusted_Connection=yes;"
#             f"ConnectionTimeout=2;"  # Быстрый таймаут для проверки
#         )
#     except Exception:
#         print("Режим 'Колледж' не сработал. Подключаемся к домашнему Docker...")
#         try:
#             return pyodbc.connect(
#                 f"Driver={{ODBC Driver 17 for SQL Server}};"
#                 f"Server=localhost,1433;"  # Твой Docker
#                 f"Database=demoappSQL;"
#                 f"UID=sa;"
#                 f"PWD=YourStrongPassword123!;"
#                 f"Encrypt=no;"
#             )
#         except Exception as e:
#             print(f"Не удалось подключиться ни к одной БД: {e}")
#             return None
#
#
# # Проверка
# conn = get_connection()
# if conn:
#     print("Соединение успешно установлено!")
#     conn.close()
