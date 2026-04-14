# import sys
# from main_window import MainWindow
# import db
# from PyQt6.QtWidgets import QApplication
# import logging
#
# def check_conn_bd():
#     try:
#         conn = db.get_conn()
#         if conn is None:
#             return False
#         conn.close()
#         return True
#     except Exception as e:
#         return False
#
# def main():
#     db_connected = check_conn_bd()
#     app = QApplication(sys.argv)
#     start_window = MainWindow(db_connected=db_connected)
#     start_window.show()
#     exit_code = app.exec()
#     sys.exit(exit_code)
#
# if __name__ == "__main__":
#     main()


import sys
from PyQt6.QtWidgets import QApplication
from register import RegisterWindow


def main():
    app = QApplication(sys.argv)

    # Создаем окно регистрации
    window = RegisterWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()