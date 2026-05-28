from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
import db_simple as db


class OrdersWindow(QWidget):
    def __init__(self, parent=None, role_name=None):
        super().__init__()
        self.setWindowTitle("Заказы")
        self.resize(850, 500)
        self.role_name = role_name
        self.init_ui()
        self.load_orders()

    def init_ui(self):
        layout = QVBoxLayout(self)
        is_admin = self.role_name and self.role_name.lower() == "администратор"

        # Определяем колонки
        cols = 6 if is_admin else 5
        headers = ["ID", "Пользователь", "Дата", "Статус", "Сумма"]
        if is_admin:
            headers.append("Действия")

        self.table = QTableWidget()
        self.table.setColumnCount(cols)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Кнопка ручного обновления списка (для удобства)
        refresh_btn = QPushButton("Обновить список")
        refresh_btn.clicked.connect(self.load_orders)
        layout.addWidget(refresh_btn)

    def load_orders(self):
        # Очищаем таблицу перед загрузкой
        self.table.setRowCount(0)

        orders = db.get_all_orders()
        self.table.setRowCount(len(orders))

        is_admin = self.role_name and self.role_name.lower() == "администратор"

        for row_idx, order in enumerate(orders):
            # Заполняем базовые текстовые поля
            oid = order.get("id")

            id_item = QTableWidgetItem(str(oid))
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 0, id_item)

            user_item = QTableWidgetItem(str(order.get("username") or "Неизвестно"))
            user_item.setFlags(user_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 1, user_item)

            date_item = QTableWidgetItem(str(order.get("order_date"))[:-3] if order.get("order_date") else "-")
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 2, date_item)

            # ОТОБРАЖЕНИЕ СТАТУСА
            current_status = str(order.get("status") or "Новый")
            if is_admin:
                # Если админ — делаем удобный выпадающий список вариантов статуса
                status_combo = QComboBox()
                status_combo.addItems(["Новый", "В обработке", "Оплачен", "Доставлен", "Отменен"])
                status_combo.setCurrentText(current_status)
                self.table.setCellWidget(row_idx, 3, status_combo)
            else:
                # Если обычный юзер — просто текст
                status_item = QTableWidgetItem(current_status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, 3, status_item)

            total_item = QTableWidgetItem(f"{float(order.get('total') or 0):.2f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 4, total_item)

            # ДЕЙСТВИЯ ДЛЯ АДМИНИСТРАТОРА (Исправлена ошибка замыкания через default-аргументы)
            if is_admin:
                save_btn = QPushButton("Сохранить")
                save_btn.setFixedSize(90, 28)
                save_btn.clicked.connect(lambda checked, r=row_idx, o_id=oid: self.save_order(r, o_id))

                del_btn = QPushButton("Удалить")
                del_btn.setFixedSize(90, 28)
                del_btn.setStyleSheet("background-color: #ff4d4d; color: white; font-weight: bold;")
                del_btn.clicked.connect(lambda checked, o_id=oid: self.delete_order(o_id))

                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(2, 2, 2, 2)
                action_layout.addWidget(save_btn)
                action_layout.addWidget(del_btn)

                action_widget = QWidget()
                action_widget.setLayout(action_layout)
                self.table.setCellWidget(row_idx, 5, action_widget)

    def save_order(self, row_idx, order_id):
        # Находим QComboBox со статусом в нужной строке
        status_widget = self.table.cellWidget(row_idx, 3)
        if isinstance(status_widget, QComboBox):
            new_status = status_widget.currentText().strip()
        else:
            return

        if db.update_order_status(order_id, new_status):
            QMessageBox.information(self, "Успех", f"Статус заказа #{order_id} обновлен на '{new_status}'")
            self.load_orders()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось обновить статус заказа")

    def delete_order(self, order_id):
        if not (self.role_name and self.role_name.lower() == "администратор"):
            return

        # Запрашиваем подтверждение перед удалением (хороший тон в UX)
        confirm = QMessageBox.question(
            self, "Удаление", f"Вы уверены, что хотите полностью удалить заказ #{order_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if db.delete_order(order_id):
                QMessageBox.information(self, "Успех", f"Заказ #{order_id} успешно удален")
                self.load_orders()  # Перезагружаем таблицу
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить заказ из БД")