from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QComboBox,
                             QPushButton, QLabel, QHBoxLayout, QFormLayout, QMessageBox)
import db

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(300, 250)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.username = QLineEdit(placeholderText="Логин")
        self.password = QLineEdit(placeholderText="Пароль", echoMode=QLineEdit.EchoMode.Password)

        form.addRow(self.username)
        form.addRow(self.password)

        self.btn_login = QPushButton("Войти")
        self.btn_login.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; height: 30px;")

        self.btn_to_reg = QPushButton("Нет аккаунта? Регистрация")
        self.btn_to_reg.setStyleSheet("border: none; color: #aaa; text-decoration: underline;")

        layout.addLayout(form)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_to_reg)

        self.btn_login.clicked.connect(self.auth)
        self.btn_to_reg.clicked.connect(self.open_reg)

    def auth(self):
        u, p = self.username.text().strip(), self.password.text().strip()
        user_data = db.login_user(u, p)

        if user_data:
            from main_window import MainWindow  # Убедитесь, что имя класса MainWindow
            self.main_win = MainWindow(user_data['username'], user_data['role_name'])
            self.main_win.show()
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")

    def open_reg(self):
        from register import RegisterWindow
        self.reg_win = RegisterWindow()
        self.reg_win.show()
        self.close()