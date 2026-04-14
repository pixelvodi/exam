from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QComboBox,
                             QPushButton, QLabel, QHBoxLayout, QFormLayout, QMessageBox)
import db


class RegisterWindow(QWidget):
    ADMIN_SECRET = "123a"
    MANAGER_SECRET = "123m"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setFixedSize(350, 450)

        self.username = QLineEdit(placeholderText="Имя пользователя")
        self.email = QLineEdit(placeholderText="Почта")
        self.password = QLineEdit(placeholderText="Пароль", echoMode=QLineEdit.EchoMode.Password)

        self.comboRoles = QComboBox()
        self.comboRoles.addItems(["Пользователь", "Менеджер", "Администратор"])

        self.code = QLineEdit(placeholderText="Код доступа", echoMode=QLineEdit.EchoMode.Password)
        self.code.hide()

        self.btn_reg = QPushButton("Зарегистрироваться")

        form = QFormLayout()
        form.addRow(self.username)
        form.addRow(self.email)
        form.addRow(self.password)
        form.addRow(self.comboRoles)
        form.addRow(self.code)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.btn_reg)

        self.btn_to_login = QPushButton("Уже есть аккаунт? Войти")
        self.btn_to_login.setStyleSheet("border: none; color: #aaa;")
        layout.addWidget(self.btn_to_login)

        self.btn_to_login.clicked.connect(self.open_login)
        self.comboRoles.currentTextChanged.connect(self.toggle_code_field)
        self.btn_reg.clicked.connect(self.registration)

    def toggle_code_field(self, role):
        self.code.setVisible(role in ["Администратор", "Менеджер"])
        if not self.code.isVisible():
            self.code.clear()

    def registration(self):
        u, e, p = self.username.text().strip(), self.email.text().strip(), self.password.text().strip()
        role_name = self.comboRoles.currentText()
        entered_code = self.code.text().strip()

        if not u or not p:
            QMessageBox.warning(self, "Ошибка", "Заполните имя и пароль")
            return

        if role_name == "Администратор" and entered_code != self.ADMIN_SECRET:
            QMessageBox.warning(self, "Ошибка", "Неверный код администратора")
            return
        elif role_name == "Менеджер" and entered_code != self.MANAGER_SECRET:
            QMessageBox.warning(self, "Ошибка", "Неверный код менеджера")
            return

        r_id = db.get_role_id(role_name)

        if db.add_user(u, e, p, r_id):
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно")
            try:
                from main_window import MainWindow
                self.main_win = MainWindow(u, role_name)
                self.main_win.show()
                self.close()
            except Exception as ex:
                QMessageBox.critical(self, "Ошибка", f"Ошибка открытия окна: {ex}")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить пользователя")

    def open_login(self):
        from login import LoginWindow
        self.log_win = LoginWindow()
        self.log_win.show()
        self.close()