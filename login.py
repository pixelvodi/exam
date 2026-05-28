from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer
import db_simple as db

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.setFixedSize(300, 200)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn = QPushButton("Войти")
        self.register_label = QLabel("Нет аккаунта?")
        self.register_btn = QPushButton("Регистрация")
        self.register_btn.setStyleSheet("border:none; color:blue; text-decoration:underline")

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.register_label)
        hbox.addWidget(self.register_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Вход"))
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(self.btn)
        layout.addLayout(hbox)

        self.btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.open_register_window)

    def login(self):
        try:
            email = self.email.text().strip().lower()
            password = self.password.text()
            ok, result = db.login_user(email, password)
            if ok and isinstance(result, dict):
                from main_window import MainApp
                self.main_window = MainApp(result['username'], result['role_name'])
                self.main_window.show()
                QTimer.singleShot(50, self.hide)
            else:
                QMessageBox.critical(self, "Ошибка", result)
        except Exception as e:
            print(str(e))

    def open_register_window(self):
        from register import RegisterApp
        self.register_window = RegisterApp(db_connected=True)
        self.register_window.show()
        self.hide()