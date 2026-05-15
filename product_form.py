import os
import shutil
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QFormLayout, QHBoxLayout, QComboBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import db_simple as db


class ProductFormWindow(QWidget):
    def __init__(self, product_id=None, parent=None):
        super().__init__()
        self.product_id = product_id
        self.parent = parent
        self.image_path = None
        self.setWindowTitle("Редактирование товара" if product_id else "Добавление товара")
        self.setFixedSize(400, 500)
        self.init_ui()
        if product_id:
            self.load_product()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.stock_input = QLineEdit()
        self.description_input = QTextEdit()
        
        self.brand_input = QComboBox()
        self.brand_input.addItem("", None)
        for b in db.get_all_brands():
            self.brand_input.addItem(b['name'], b['id'])
        
        self.color_input = QComboBox()
        self.color_input.addItem("", None)
        for c in db.get_all_colors():
            self.color_input.addItem(c['name'], c['id'])

        self.size_input = QLineEdit()

        self.img_label = QLabel("Нет фото")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setFixedSize(200, 150)
        self.img_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        self.img_btn = QPushButton("Выбрать изображение")
        self.img_btn.clicked.connect(self.select_image)

        form.addRow("Название:", self.name_input)
        form.addRow("Цена:", self.price_input)
        form.addRow("Количество:", self.stock_input)
        form.addRow("Описание:", self.description_input)
        form.addRow("Бренд:", self.brand_input)
        form.addRow("Цвет:", self.color_input)
        form.addRow("Размер:", self.size_input)
        form.addRow("Изображение:", self.img_label)
        form.addRow("", self.img_btn)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_product)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_product(self):
        product = db.get_product_by_id(self.product_id)
        if not product:
            return

        self.name_input.setText(product.get("name", ""))
        self.price_input.setText(str(product.get("price", "")))
        self.stock_input.setText(str(product.get("stock_quantity", 0)))
        self.description_input.setText(product.get("description", ""))
        self.size_input.setText(product.get("size", ""))

        brand_id = product.get("brand_id")
        color_id = product.get("color_id")
        
        for i in range(self.brand_input.count()):
            if self.brand_input.itemData(i) == brand_id:
                self.brand_input.setCurrentIndex(i)
                break
        
        for i in range(self.color_input.count()):
            if self.color_input.itemData(i) == color_id:
                self.color_input.setCurrentIndex(i)
                break

        self.image_path = product.get("image_url")
        if self.image_path and os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.img_label.setPixmap(pixmap)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.image_path = path
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.img_label.setPixmap(pixmap)

    def _save_image(self):
        if self.image_path and os.path.exists(self.image_path) and not self.image_path.startswith("public/img/"):
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            images_folder = os.path.join(BASE_DIR, "public", "img")
            os.makedirs(images_folder, exist_ok=True)
            filename = os.path.basename(self.image_path)
            destination = os.path.join(images_folder, filename)
            shutil.copy(self.image_path, destination)
            self.image_path = f"public/img/{filename}"
        return self.image_path

    def save_product(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        stock = self.stock_input.text().strip()
        description = self.description_input.toPlainText().strip()
        brand_id = self.brand_input.currentData()
        color_id = self.color_input.currentData()
        size = self.size_input.text().strip()

        if not name or not price:
            return QMessageBox.warning(self, "Ошибка", "Заполните название и цену")

        try:
            price = float(price)
        except:
            return QMessageBox.warning(self, "Ошибка", "Цена должна быть числом")

        stock = int(stock or 0)

        image_url = self._save_image()

        if self.product_id:
            ok = db.update_product_full(self.product_id, name, price, description, image_url, brand_id, color_id, size, stock)
            msg = "Товар обновлен"
        else:
            ok, msg = db.add_product(name, price, stock, description, image_url, brand_id, color_id, size)

        if ok:
            QMessageBox.information(self, "Успех", msg)
            if self.parent and hasattr(self.parent, "load_products"):
                QTimer.singleShot(100, self.parent.load_products)
            self.close()
        else:
            QMessageBox.critical(self, "Ошибка", msg if isinstance(msg, str) else "Не удалось сохранить товар")