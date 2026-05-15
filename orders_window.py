from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
import db_simple as db


class OrdersWindow(QWidget):
    def __init__(self, parent=None, role_name=None):
        super().__init__()
        self.setWindowTitle("Заказы")
        self.resize(800, 500)
        self.role_name = role_name
        self.init_ui()
        self.load_orders()

    def init_ui(self):
        layout = QVBoxLayout(self)
        is_admin = self.role_name and self.role_name.lower() == "администратор"
        cols = 6 if is_admin else 5
        headers = ["ID", "Пользователь", "Дата", "Статус", "Сумма"] + (["Действия"] if is_admin else [])

        self.table = QTableWidget()
        self.table.setColumnCount(cols)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def load_orders(self):
        orders = db.get_all_orders()
        self.table.setRowCount(len(orders))
        for row_idx, order in enumerate(orders):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(order.get("id"))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(order.get("username"))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(order.get("order_date"))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(order.get("status"))))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(order.get("total"))))

            if self.role_name and self.role_name.lower() == "администратор":
                save_btn = QPushButton("Сохранить")
                save_btn.setFixedSize(100, 35)
                save_btn.clicked.connect(lambda checked, row=row_idx, oid=order["id"]: self.save_order(row, oid))

                del_btn = QPushButton("Удалить")
                del_btn.setFixedSize(100, 35)
                del_btn.clicked.connect(lambda checked, oid=order["id"]: self.delete_order(oid))

                action_layout = QHBoxLayout()
                action_layout.addWidget(save_btn)
                action_layout.addWidget(del_btn)

                action_widget = QWidget()
                action_widget.setLayout(action_layout)
                self.table.setCellWidget(row_idx, 5, action_widget)

    def save_order(self, row_idx, order_id):
        new_status = self.table.item(row_idx, 3).text().strip()
        if not new_status:
            return QMessageBox.warning(self, "Ошибка", "Статус не может быть пустым")
        if db.update_order_status(order_id, new_status):
            QMessageBox.information(self, "Успех", f"Заказ #{order_id} обновлен")
            self.load_orders()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось обновить заказ")

    def delete_order(self, order_id):
        if not (self.role_name and self.role_name.lower() == "администратор"):
            return
        db.delete_order(order_id)
        self.load_orders()