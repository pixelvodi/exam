from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIntValidator  # Для валидации ввода количества
from PyQt6.QtCore import Qt
import db_simple as db  # Или просто import db, если файл называется db.py


class CreateOrderWindow(QWidget):
    def __init__(self, parent=None, username=None):
        super().__init__()
        self.parent = parent
        self.username = username
        self.setWindowTitle("Создать заказ")
        self.resize(350, 250)  # Задаем аккуратный размер окна

        # 1. Выпадающий список товаров
        self.combo_product = QComboBox()
        self.combo_product.setPlaceholderText("Товар")

        # 2. Метки для отображения цен
        self.price_per_item = QLabel("Цена за ед.: -")
        self.total_price_label = QLabel("Общая цена: 0.00")

        # Загружаем товары из БД (используем get_all_products из прошлого шага)
        self.all_products = db.get_all_products()
        self.combo_product.addItem("Выберите товар", None)
        for p in self.all_products:
            # Сохраняем весь объект товара (словарь) в userData ячейки
            self.combo_product.addItem(p['name'], p)

            # Привязываем изменение выбора к пересчету цены
        self.combo_product.currentIndexChanged.connect(self.update_price_and_total)

        # 3. Текстовое поле для размера
        self.size = QLineEdit()
        self.size.setPlaceholderText("Размер")

        # 4. Текстовое поле для количества + валидатор целых чисел
        self.count = QLineEdit()
        self.count.setPlaceholderText("Кол-во")
        self.count.setValidator(QIntValidator(1, 9999))
        # Привязываем изменение текста количества к пересчету цены
        self.count.textChanged.connect(self.update_price_and_total)

        # 5. Кнопка создания заказа
        self.add_order = QPushButton("Создать заказ")
        self.add_order.clicked.connect(self.create_order)

        # Компонуем интерфейс (вертикально, один под другим)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.combo_product)
        self.main_layout.addWidget(self.price_per_item)
        self.main_layout.addWidget(self.size)
        self.main_layout.addWidget(self.count)
        self.main_layout.addWidget(self.total_price_label)
        self.main_layout.addWidget(self.add_order)

        # Первичный запуск для сброса меток в дефолтное состояние
        self.update_price_and_total()

    def update_price_and_total(self):
        """Обновляет отображение цены за единицу и общей цены."""
        selected_product = self.combo_product.currentData()
        quantity_str = self.count.text().strip()

        quantity = 0
        if quantity_str:
            try:
                quantity = int(quantity_str)
            except ValueError:
                quantity = 0

        # Если товар выбран и у него есть цена
        if selected_product and selected_product.get('price') is not None:
            price_val = float(selected_product['price'])
            self.price_per_item.setText(f"Цена за ед.: {price_val:.2f}")

            total_price = price_val * quantity
            self.total_price_label.setText(f"Общая цена: {total_price:.2f}")
        else:
            self.price_per_item.setText("Цена за ед.: -")
            self.total_price_label.setText("Общая цена: 0.00")

    def create_order(self):
        if not self.username:
            QMessageBox.critical(self, "Ошибка", "Пользователь не авторизован")
            return

        selected_product = self.combo_product.currentData()
        if not selected_product:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите товар из списка")
            return

        quantity_str = self.count.text().strip()
        if not quantity_str or int(quantity_str) <= 0:
            QMessageBox.warning(self, "Предупреждение", "Укажите корректное количество товара")
            return

        try:
            # 1. Сначала находим ID пользователя по его username
            user = db.get_user_by_username(self.username)
            if not user:
                return QMessageBox.critical(self, "Ошибка", "Пользователь не найден в БД")

            # 2. Формируем список из ОДНОГО товара в том формате, который ждет функция create_order
            items = [{
                'product_id': selected_product['id'],
                'quantity': int(quantity_str),
                'size': self.size.text().strip()
            }]

            # 3. Вызываем обновленную функцию создания заказа
            ok = db.create_order(user['id'], items)

            if ok:
                QMessageBox.information(self, "Успех", "Заказ успешно создан!")
                self.close()  # Закрываем окошко после успеха
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить заказ в базе данных")

        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Что-то пошло не так: {str(e)}")