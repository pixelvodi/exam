from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QSpinBox, QMessageBox
import db_simple as db


class CreateOrderWindow(QWidget):
    def __init__(self, parent=None, username=None):
        super().__init__()
        self.setWindowTitle("Создать заказ")
        self.resize(600, 400)
        self.username = username

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Товар", "Цена", "Количество"])
        layout.addWidget(self.table)

        self.load_products()

        submit_btn = QPushButton("Оформить заказ")
        submit_btn.clicked.connect(self.submit_order)
        layout.addWidget(submit_btn)

    def load_products(self):
        products = db.get_all_products()
        self.table.setRowCount(len(products))
        for i, p in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(p['name']))
            self.table.setItem(i, 1, QTableWidgetItem(str(p['price'])))
            spin = QSpinBox()
            spin.setMaximum(100)
            spin.setValue(0)
            self.table.setCellWidget(i, 2, spin)

    def submit_order(self):
        if not self.username:
            return

        user = db.get_user_by_username(self.username)
        if not user:
            return QMessageBox.critical(self, "Ошибка", "Пользователь не найден")

        items = []
        for i in range(self.table.rowCount()):
            spin = self.table.cellWidget(i, 2)
            if not spin or spin.value() <= 0:
                continue
            name_item = self.table.item(i, 0)
            if not name_item:
                continue
            product = db.get_product_by_name(name_item.text())
            if product:
                items.append({'product_id': product['id'], 'quantity': spin.value()})

        if not items:
            return QMessageBox.information(self, "Информация", "Не выбрано ни одного товара")

        success = db.create_order(user['id'], items)
        if success:
            QMessageBox.information(self, "Успех", "Заказ создан")
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось создать заказ")