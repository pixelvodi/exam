# from PyQt6.QtWidgets import (QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QMessageBox, QHBoxLayout,
#                              QFormLayout, QWidget)
# import db
# from PyQt6.QtCore import QTimer
#
# admin_code = "123a"
# manager_code = "123a"
# roles = ["Администратор", "Менеджер", "Пользователь"]
#
# class RegisterApp(QWidget):
#     def __init__(self, db_connected=False):
#         super().__init__()
#         self.db_connected = db_connected
#         self.status = QLabel("Бд подключена" if db_connected else "Нет бд")
#         self.setWindowTitle("Регистрация")
#         self.setFixedSize(300, 400)
#
#         self.username = QLineEdit()
#         self.username.setPlaceholderText("Имя пользователя")
#
#         self.email = QLineEdit()
#         self.email.setPlaceholderText("Почта")
#
#         self.password = QLineEdit()
#         self.password.setEchoMode(QLineEdit.EchoMode.Password)
#         self.password.setPlaceholderText("Пароль")
#
#         self.comboRoles = QComboBox()
#         self.comboRoles.addItems(roles)
#
#         self.code = QLineEdit()
#         self.code.setEchoMode(QLineEdit.EchoMode.Password)
#         self.code.setPlaceholderText("Пароль от роли")
#         self.code.hide()
#
#         self.btn_reg = QPushButton("Регистарция")
#
#         self.login_label = QLabel("Есть аккаунт?")
#         self.login_btn = QPushButton("Войти")
#
#         hbox = QHBoxLayout()
#         hbox.addWidget(self.login_label)
#         hbox.addWidget(self.login_btn)
#
#         form = QFormLayout()
#         form.addRow(self.username)
#         form.addRow(self.email)
#         form.addRow(self.password)
#         form.addRow(self.comboRoles)
#         form.addRow(self.code)
#         form.addRow(hbox)
#
#         main_layout = QVBoxLayout(self)
#         main_layout.addWidget(self.status)
#         main_layout.addLayout(form)
#         main_layout.addWidget(self.btn_reg)
#
#         self.comboRoles.currentTextChanged.connect(lambda r: self.code.setVisible(r.lower() in ["менеджер", "администратор"]))
#         self.comboRoles.currentTextChanged.connect(lambda r: self.code.setPlaceholderText(f"Код для {r}"))
#         self.btn_reg.clicked.connect(self.registration)
#         self.login_btn.clicked.connect(self.login_window)
#
#     def registration(self):
#         u, e, p = self.username.text().strip(), self.email.text().strip(), self.password.text().strip()
#         r, c = self.comboRoles.currentText(), self.code.text().strip()
#
#         ok, msg = db.add_user(u, e, r, p)
#         if ok:
#             from main_window import MainApp
#             main_window = MainApp(u, r)
#             main_window.show()
#             QTimer.singleShot(50, self.hide)
#         else:
#             QMessageBox.critical(self, "Ошибка", msg)
#
#     def login_window(self):
#         from login import LoginApp
#         self.login_window = LoginApp()
#         self.login_window.show()
#         self.hide()

from PyQt6.QtWidgets import *
import db_simple as db

admin_code = "123a"
manager_code = "123m"
roles = ["Администратор", "Менеджер", "Пользователь"]

class RegisterApp(QWidget):
    def __init__(self, db_connected=False):
        super().__init__()
        self.db_connected = db_connected
        self.status = QLabel("DB have" if db_connected else "DB no")
        self.setWindowTitle("Регистрация")
        self.setFixedSize(300, 400)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Имя")

        self.email = QLineEdit()
        self.email.setPlaceholderText("почта")

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("пароль")

        self.comboRoles = QComboBox()
        self.comboRoles.addItems(roles)

        self.code = QLineEdit()
        self.code.setEchoMode(QLineEdit.EchoMode.Password)
        self.code.setPlaceholderText("пароль для роли")
        self.code.hide()

        self.btn_reg = QPushButton("Регистрация")

        self.login_label = QLabel("Есть аккаунт?")
        self.login_btn = QPushButton("Войти")

        hbox = QHBoxLayout()
        hbox.addWidget(self.login_label)
        hbox.addWidget(self.login_btn)

        form = QFormLayout()
        form.addRow(self.username)
        form.addRow(self.email)
        form.addRow(self.password)
        form.addRow(self.comboRoles)
        form.addRow(self.code)
        form.addRow(hbox)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.status)
        main_layout.addLayout(form)
        main_layout.addWidget(self.btn_reg)

        self.comboRoles.currentTextChanged.connect(lambda r: self.code.setVisible(r.lower() in ["менеджер", "администратор"]))
        self.comboRoles.currentTextChanged.connect(lambda r: self.code.setPlaceholderText(f"Код для роли {r}"))
        self.btn_reg.clicked.connect(self.registration)
        self.login_btn.clicked.connect(self.login_window)

    def registration(self):
        u, e, p = self.username.text().strip(), self.email.text().strip(), self.password.text().strip()
        r, c = self.comboRoles.currentText(), self.code.text().strip()

        ok, msg = db.add_user(u, e, r, p)
        if ok:
            from main_window import MainApp
            main_window = MainApp(u, r)
            main_window.show()
        else:
            QMessageBox.critical(self, "Ошбика", msg)

    def login_window(self):
        from login import LoginApp
        self.login_window = LoginApp()
        self.login_window.show()
        self.hide()




