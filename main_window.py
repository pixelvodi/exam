import os
from functools import partial
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout, QScrollArea,
    QPushButton, QFrame, QLineEdit, QComboBox, QHBoxLayout, QSplitter
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import db_simple as db


def _create_product_card(product, role_name, edit_callback=None, delete_callback=None):
    card = QFrame()
    card.setFixedHeight(200)

    discount = product.get("discount", 0) or 0
    quantity = product.get("stock_quantity", 0) or 0
    old_price_db = product.get("old_price")
    base_price = product.get("price", 0)

    DEMO_DISCOUNT_PERCENT = 15
    if discount == 0:
        discount = DEMO_DISCOUNT_PERCENT

    bg_color = "#2d2d2d"
    border_color = "#404040"
    if discount >= 15:
        bg_color = "#1e4d2b"
    if quantity == 0:
        bg_color = "#4d2d2d"

    card.setStyleSheet(f"""
        QFrame {{ background-color: {bg_color}; border-radius: 8px; border: 2px solid {border_color}; }}
        QFrame:hover {{ border: 2px solid #0078d7; }}
    """)

    main_layout = QHBoxLayout(card)
    main_layout.setContentsMargins(15, 10, 15, 10)
    main_layout.setSpacing(20)

    photo_frame = QFrame()
    photo_frame.setFixedSize(160, 160)
    photo_frame.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 4px; border: 1px solid #cccccc; }")
    photo_layout = QVBoxLayout(photo_frame)
    photo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    img_label = QLabel()
    img_label.setFixedSize(140, 140)
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    img_label.setStyleSheet("background-color: #f0f0f0;")

    image_path = product.get("image_url")
    if image_path:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(BASE_DIR, image_path)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                img_label.setPixmap(pixmap)
            else:
                img_label.setText("Фото")
        else:
            img_label.setText("Фото")
    else:
        img_label.setText("Фото")

    photo_layout.addWidget(img_label)
    main_layout.addWidget(photo_frame)

    info_layout = QVBoxLayout()
    info_layout.setSpacing(5)

    category = product.get("category", "")
    name = product.get("name", "")
    header_label = QLabel(f"{category} | {name}")
    header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
    header_label.setStyleSheet("color: #ffffff;")
    header_label.setWordWrap(True)
    info_layout.addWidget(header_label)

    description = product.get("description", "")
    if description:
        desc_label = QLabel(f"Описание товара: {description}")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #dddddd; font-size: 11px;")
        info_layout.addWidget(desc_label)

    manufacturer = product.get("manufacturer", "")
    if manufacturer:
        manuf_label = QLabel(f"Производитель: {manufacturer}")
        manuf_label.setStyleSheet("color: #cccccc; font-size: 10px;")
        info_layout.addWidget(manuf_label)

    supplier = product.get("supplier", "")
    if supplier:
        suppl_label = QLabel(f"Поставщик: {supplier}")
        suppl_label.setStyleSheet("color: #cccccc; font-size: 10px;")
        info_layout.addWidget(suppl_label)

    price_layout = QHBoxLayout()
    price_layout.setSpacing(10)

    final_price = base_price
    if old_price_db and old_price_db > base_price:
        display_old_price = old_price_db
        display_new_price = base_price
    elif discount > 0:
        display_old_price = base_price
        final_price = base_price * (100 - discount) / 100
        display_new_price = final_price
    else:
        display_old_price = None
        display_new_price = base_price

    if display_old_price:
        old_price_label = QLabel(f"{display_old_price} ₽")
        old_price_label.setStyleSheet("color: #ff4444; font-size: 14px; text-decoration: line-through;")
        price_layout.addWidget(old_price_label)

        new_price_label = QLabel(f"{display_new_price:.0f} ₽")
        new_price_label.setStyleSheet("color: #28a745; font-size: 18px; font-weight: bold;")
        price_layout.addWidget(new_price_label)
    else:
        price_label = QLabel(f"Цена: {display_new_price} ₽")
        price_label.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        price_layout.addWidget(price_label)

    price_layout.addStretch()
    info_layout.addLayout(price_layout)

    unit = product.get("unit", "шт.")
    qty_label = QLabel(f"Единица измерения: {unit} | Количество на складе: {quantity}")
    qty_label.setStyleSheet("color: #aaaaaa; font-size: 10px;")
    info_layout.addWidget(qty_label)

    info_layout.addStretch()
    main_layout.addLayout(info_layout, 1)

    discount_frame = QFrame()
    discount_frame.setFixedSize(120, 160)
    discount_frame.setStyleSheet("QFrame { background-color: #4a4a4a; border-radius: 4px; border: 1px solid #666666; }")
    discount_layout = QVBoxLayout(discount_frame)
    discount_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    discount_label = QLabel(f"Действующая\nскидка\n{discount}%")
    discount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    discount_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
    discount_label.setWordWrap(True)
    discount_label.setStyleSheet("color: #ffd700; font-size: 14px;" if discount > 0 else "color: #888888; font-size: 12px;")

    discount_layout.addWidget(discount_label)
    main_layout.addWidget(discount_frame)

    if role_name and role_name.lower() == "администратор":
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        edit_btn = QPushButton("✏ Редактировать")
        edit_btn.setFixedSize(130, 30)
        edit_btn.setObjectName("edit")
        edit_btn.setStyleSheet("QPushButton { background-color: #555555; color: #ffffff; border-radius: 4px; } QPushButton:hover { background-color: #777777; }")
        if edit_callback:
            edit_btn.clicked.connect(partial(edit_callback, product.get("id")))

        delete_btn = QPushButton("🗑 Удалить")
        delete_btn.setFixedSize(100, 30)
        delete_btn.setObjectName("delete")
        delete_btn.setStyleSheet("QPushButton { background-color: #aa3333; color: #ffffff; border-radius: 4px; } QPushButton:hover { background-color: #cc4444; }")
        if delete_callback:
            delete_btn.clicked.connect(partial(delete_callback, product.get("id")))

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        info_layout.addLayout(btn_layout)

    return card


class MainApp(QWidget):
    def __init__(self, username, role_name):
        super().__init__()
        self.setWindowTitle("Главная")
        self.resize(1200, 700)
        self.username = username
        self.role_name = role_name
        self.child_windows = []
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        header = QLabel(f"Пользователь: {self.username} ({self.role_name})")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        logout_btn = QPushButton("Выйти")
        logout_btn.setFixedSize(100, 30)
        logout_btn.clicked.connect(self.logout)
        top_layout.addWidget(header)
        top_layout.addStretch()
        top_layout.addWidget(logout_btn)
        main_layout.addLayout(top_layout)

        if self.role_name and self.role_name.lower() in ["менеджер", "администратор"]:
            splitter = QSplitter(Qt.Orientation.Horizontal)
            main_layout.addWidget(splitter)

            sidebar = QFrame()
            sidebar.setStyleSheet("background-color: #333333; border-right:1px solid #555555;")
            sidebar_layout = QVBoxLayout(sidebar)
            sidebar_layout.setContentsMargins(10, 10, 10, 10)
            sidebar_layout.setSpacing(15)

            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск по названию")
            sidebar_layout.addWidget(QLabel("Поиск"))
            sidebar_layout.addWidget(self.search_input)

            self.sort_combo = QComboBox()
            self.sort_combo.addItems(["Без сортировки", "Цена выше", "Цена ниже"])
            sidebar_layout.addWidget(QLabel("Сортировка"))
            sidebar_layout.addWidget(self.sort_combo)

            filter_btn = QPushButton("Применить")
            filter_btn.clicked.connect(self.load_products)
            sidebar_layout.addWidget(filter_btn)

            orders_btn = QPushButton("📦 Заказы")
            orders_btn.clicked.connect(self.open_orders_window)
            sidebar_layout.addWidget(orders_btn)

            sidebar_layout.addStretch()

            if self.role_name and self.role_name.lower() == "администратор":
                add_btn = QPushButton("➕ Добавить товар")
                add_btn.clicked.connect(self.add_product)
                sidebar_layout.addWidget(add_btn)

            splitter.addWidget(sidebar)
            sidebar.setFixedWidth(220)

            self.container = QWidget()
            self.list_layout = QVBoxLayout(self.container)
            self.list_layout.setSpacing(15)
            self.list_layout.setContentsMargins(10, 10, 10, 10)
            self.list_layout.addStretch()

            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setWidget(self.container)
            self.scroll.setStyleSheet("border: none; background-color: transparent;")

            splitter.addWidget(self.scroll)
            splitter.setStretchFactor(1, 1)
        else:
            self.search_input = None
            self.sort_combo = None

            self.container = QWidget()
            self.list_layout = QVBoxLayout(self.container)
            self.list_layout.setSpacing(15)
            self.list_layout.setContentsMargins(10, 10, 10, 10)
            self.list_layout.addStretch()

            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setWidget(self.container)
            self.scroll.setStyleSheet("border: none; background-color: transparent;")

            main_layout.addWidget(self.scroll)

            create_order_btn = QPushButton("🛒 Создать заказ")
            create_order_btn.clicked.connect(self.create_order)
            main_layout.addWidget(create_order_btn)

        self.load_products()

    def load_products(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        search = self.search_input.text() if self.search_input else ""
        sort = self.sort_combo.currentText() if self.sort_combo else ""
        products = db.get_products(search, sort)

        for product in products:
            card = _create_product_card(product, self.role_name, self.edit_product, self.delete_product)
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)

    def add_product(self):
        from product_form import ProductFormWindow
        add_window = ProductFormWindow(parent=self)
        self.child_windows.append(add_window)
        add_window.show()

    def edit_product(self, product_id):
        from product_form import ProductFormWindow
        edit_window = ProductFormWindow(product_id, parent=self)
        self.child_windows.append(edit_window)
        edit_window.show()

    def delete_product(self, product_id):
        db.delete_product(product_id)
        self.load_products()

    def logout(self):
        from login import LoginApp
        self.login_window = LoginApp()
        self.login_window.show()
        self.close()

    def open_orders_window(self):
        from orders_window import OrdersWindow
        orders_window = OrdersWindow(parent=self, role_name=self.role_name)
        self.child_windows.append(orders_window)
        orders_window.show()

    def create_order(self):
        from create_order_window import CreateOrderWindow
        order_window = CreateOrderWindow(parent=self, username=self.username)
        self.child_windows.append(order_window)
        order_window.show()