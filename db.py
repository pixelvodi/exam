# import logging
# import pyodbc
# import os
#
# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8', force=True)
# logger = logging.getLogger(__name__)
#
# db_config = {
#     "driver": "{ODBC Driver 17 for SQL Server}",
#     "server": "localhost,1433",
#     "database": "demoappSQL",
#     "uid": "sa",
#     "pwd": "YourStrongPassword123!",
#     "ConnectionTimeout": 5
# }
#
# def get_conn():
#     try:
#         conn = pyodbc.connect(
#             f"Driver={db_config['driver']};Server={db_config['server']};Database={db_config['database']};UID={db_config['uid']};PWD={db_config['pwd']};Encrypt=yes;TrustServerCertificate=yes;")
#         return conn
#     except Exception as e:
#         logger.error(f"Ошибка подключения: {e}")
#         return None
#
# def _exec(query, params=(), fetch=True, commit=False):
#     conn = get_conn()
#     if not conn: return None if fetch else False
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute(query, params)
#             if cursor.description:
#                 cols = [c[0] for c in cursor.description]
#                 res = cursor.fetchone() if fetch else cursor.fetchall()
#                 return dict(zip(cols,res)) if fetch else ([dict(zip(cols, r)) for r in res] if res else [])
#             if commit: conn.commit()
#             return None if fetch else True
#     except Exception as e:
#         return None if fetch else False
#     finally:
#         conn.close()
#
# def get_user():
#     # Убираем WHERE, если хотим весь список.
#     # Пишем [user] в скобках, так как это зарезервированное слово в SQL Server.
#     sql = "SELECT u.id, u.username, u.password, u.role_id, u.email, r.role_name FROM [users] u INNER JOIN roles r ON u.role_id = r.id"
#     return _exec(sql, params=(), fetch=False) or []
#
#
# def update_user(user_id, username, email, role_id, password):
#     try:
#         # WHERE id=? говорит базе: "ищи человека с этим паспортом"
#         # SET ... меняет всё остальное, кроме самого ID
#         sql = "UPDATE [users] SET username=?, email=?, role_id=?, password=? WHERE id=?"
#
#         # Важно: количество знаков ? должно совпадать с количеством элементов в скобках
#         params = (username, email, int(role_id), password, user_id)
#
#         return _exec(sql, params, fetch=False, commit=True)
#     except Exception as e:
#         logger.error(f"Ошибка UPDATE: {e}")
#         return False
#
# def delete_user(user_id): _exec("DELETE FROM users WHERE id=?",user_id, commit=True)
#
# def get_products():
#     # ОБЯЗАТЕЛЬНО добавляем image_url в SELECT
#     sql, params = "SELECT id, name, price, stock_quantity, description, size, image_url FROM products WHERE 1=1", []
#     return _exec(sql, params, fetch=False) or []
#
#
# def update_products(product_id, name, price, stock_quantity, description, size, image_url):
#     try:
#         # Если пришел полный путь, берем только имя файла
#         file_name = os.path.basename(image_url)
#         # Формируем путь для БД (как на скриншоте)
#         db_path = f"public/img/{file_name}"
#
#         sql = "UPDATE products SET name=?, price=?, stock_quantity=?, description=?, size=?, image_url=? WHERE id=?"
#
#         # Приводим типы данных, чтобы SQL не ругался
#         params = (
#         name, float(str(price).replace(',', '.')), int(stock_quantity), description, size, db_path, product_id)
#
#         return _exec(sql, params, fetch=False, commit=True)
#     except Exception as e:
#         print(f"ОШИБКА В DB.PY: {e}")
#         return False
#
# def update_product_image(product_id, image_url):
#     try:
#         sql = "UPDATE products SET image_url=? WHERE id=?"
#         return _exec(sql, (image_url, product_id), fetch=False, commit=True)
#     except Exception as e:
#         logger.error(f"Ошибка обновления картинки: {e}")
#         return False
#
# def delete_product(product_id): _exec("DELETE FROM products WHERE id=?", product_id, commit=True)
#
#
# def add_user(username, email, password, role_id):
#     sql = "INSERT INTO [users] (username, email, password, role_id) VALUES (?, ?, ?, ?)"
#     params = (username, email, password, int(role_id))
#     return _exec(sql, params, fetch=False, commit=True)
#
#
# def add_product(name, price, stock, desc, size, image_url):
#     file_name = os.path.basename(image_url)
#     db_path = f"public/img/{file_name}" if file_name else "public/img/default.jpg"
#
#     sql = "INSERT INTO products (name, price, stock_quantity, description, size, image_url) VALUES (?, ?, ?, ?, ?, ?)"
#     params = (name, float(str(price).replace(',', '.')), int(stock), desc, size, db_path)
#     return _exec(sql, params, fetch=False, commit=True)


import pyodbc
import os

db_config = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "localhost,1433",
    "database": "demoappSQL",
    "uid": "sa",
    "pwd": "YourStrongPassword123!",
    "ConnectionTimeOut": 5
}


def get_conn():
    try:
        # Добавьте TrustServerCertificate=yes, если используете локальный SQL Server без SSL
        conn = pyodbc.connect(
            f"Driver={db_config['driver']};Server={db_config['server']};Database={db_config['database']};UID={db_config['uid']};PWD={db_config['pwd']};Encrypt=yes;TrustServerCertificate=yes;")
        return conn
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None


def _execute(query, params=(), fetch=True, commit=False):
    conn = get_conn()
    if conn is None: return None if fetch else False
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if commit: conn.commit()

            if cursor.description:
                cols = [c[0] for c in cursor.description]
                if fetch:
                    res = cursor.fetchone()
                    return dict(zip(cols, res)) if res else None
                else:
                    res = cursor.fetchall()
                    return [dict(zip(cols, r)) for r in res] if res else []
            return True
    except Exception as e:
        print(f"Ошибка SQL: {e}")
        return None if fetch else False
    finally:
        conn.close()  # Важно закрывать именно тут


def add_user(username, email, password, role_id):
    # Указываем таблицу [users] (в скобках, так как user - зарезервированное слово)
    sql = "INSERT INTO [users] (username, email, password, role_id) VALUES (?, ?, ?, ?)"
    params = (username, email, password, int(role_id))
    return _execute(sql, params, fetch=False, commit=True)


# Функция для получения ID роли по названию
def get_role_id(role_name):
    res = _execute("SELECT id FROM roles WHERE role_name = ?", (role_name,), fetch=True)
    return res['id'] if res else 3  # 3 - по умолчанию Пользователь

def get_user():
    sql = "SELECT u.id, u.username, u.password, u.role_id, u.email, r.role_name FROM users u INNER JOIN roles r ON u.role_id = r.id"
    return _execute(sql, params=(), fetch=False) or []

def update_user(user_id, username, email, role_id, password):
    try:
        sql = "UPDATE users SET username=?, email=?, role_id=?, password=? WHERE id=?"
        params = (username, email, int(role_id), password, user_id)
        return _execute(sql, params, fetch=False, commit=True)
    except Exception as e:
        return False

def delete_user(user_id): return _execute("DELETE FROM users WHERE id=?", user_id, commit=True)

def get_products():
    sql, params = "SELECT id, name, price, stock_quantity, description, size, image_url FROM products WHERE 1=1", []
    return _execute(sql, params, fetch=False) or []

def update_products(product_id, name, price, stock_quantity, description, size, image_url):
    try:
        file_name = os.path.basename(image_url)
        db_path = f"public/img/{file_name}"

        sql = "UPDATE products SET name=?, price=?, stock_quantity=?, description=?, size=? image_url=? WHERE id=?"

        params = (name, float(str(price).replace(',', '.')), int(stock_quantity), description, size, db_path, product_id)

        return _execute(sql, params, fetch=False, commit=True)
    except Exception as e:
        return False

def update_products_image(product_id, image_url):
    try:
        sql = "UPDATE products SET image_url=? WHERE id=?"
        return _execute(sql, (image_url, product_id), fetch=False, commit=True)
    except Exception as e:
        return False

def delete_product(product_id): return _execute("DELETE FROM products WHERE id=?", product_id, commit=True)

# def add_user(username, email, password, role_id):
#     sql = "INSERT INTO users (username, email, password, role_id) VALUES (?, ?, ?, ?)"
#     params = (username, email, password, int(role_id))
#     return _execute(sql, params, fetch=False, commit=True)

def add_products(name, price, stock, desc, size, image_url):
    file_name = os.path.basename(image_url)
    db_path = f"public/img/{file_name}" if file_name else f"public/img/default.jpg"

    sql = "INSERT INTO products (name, price, stock_quantity, size, image_url) VALUES (?, ?, ?, ?, ?)"
    params = (name, float(str(price).replace(',','.')), stock, stock, db_path)
    return _execute(sql, params, fetch=False, commit=True)

def login_user(username, password):
    """Проверяет данные пользователя и возвращает инфо, если всё ок"""
    sql = """
        SELECT u.username, r.role_name 
        FROM [users] u 
        INNER JOIN roles r ON u.role_id = r.id 
        WHERE u.username = ? AND u.password = ?
    """
    return _execute(sql, (username, password), fetch=True)