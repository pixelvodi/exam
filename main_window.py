from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QScrollArea
import db
import os
from PyQt6.QtGui import QPixmap # Добавьте этот импорт в начало файла
from PyQt6.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self, db_connected=False):
        super().__init__()
        self.db_connected = db_connected
        self.setWindowTitle("Главное окно")
        self.setFixedSize(1200, 1000)

        self.main_layout = QVBoxLayout(self)

        self.users_list_layout = QVBoxLayout()
        self.products_list_layout = QVBoxLayout()

        self.init_ui()
        self.load_users()
        self.load_products()

    def init_ui(self):
        self.main_layout.addWidget(QLabel("<b>Список пользователей:</b>"))

        self.users_container = QWidget()
        self.users_container.setLayout(self.users_list_layout)  # Привязываем макет пользователей
        self.main_layout.addWidget(self.users_container)

        self.main_layout.addWidget(QLabel("<hr>"))  # Разделительная линия

        self.main_layout.addWidget(QLabel("<b>Список товаров:</b>"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        self.products_container = QWidget()
        self.products_container.setLayout(self.products_list_layout)  # Привязываем макет товаров
        self.products_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.products_container)
        self.main_layout.addWidget(scroll)

    def load_users(self):
        while self.users_list_layout.count():
            item = self.users_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_sub_layout(item.layout())

        users = db.get_user()
        if not users:
            self.users_list_layout.addWidget(QLabel("Список пользователей пуст"))
            return

        add_widget = QWidget()
        add_layout = QHBoxLayout(add_widget)

        new_u = QLineEdit()
        new_u.setPlaceholderText("Имя")
        new_e = QLineEdit()
        new_e.setPlaceholderText("Почта")
        new_p = QLineEdit()
        new_p.setPlaceholderText("Пароль")
        new_r = QLineEdit()
        new_r.setPlaceholderText("ID Роли (1 или 2)")

        btn_add = QPushButton("➕ Добавить")
        btn_add.setStyleSheet("background-color: #2d5a35; color: white; font-weight: bold;")

        def confirm_add_user():
            if db.add_user(new_u.text(), new_e.text(), new_p.text(), new_r.text()):
                self.load_users()

        btn_add.clicked.connect(confirm_add_user)

        for w in [new_u, new_e, new_p, new_r]: add_layout.addWidget(w)
        add_layout.addWidget(btn_add)
        self.users_list_layout.addWidget(add_widget)
        self.users_list_layout.addWidget(QLabel("<hr>"))

        for user in users:
            row_widget = QWidget()
            header_layout = QHBoxLayout(row_widget)  # Привязываем макет к виджету сразу

            edit_username = QLineEdit(str(user.get('username', '')))
            edit_email = QLineEdit(str(user.get('email', '')))
            edit_password = QLineEdit(str(user.get('password', '')))
            edit_role_id = QLineEdit(str(user.get('role_id', '')))

            fields = [edit_username, edit_email, edit_password, edit_role_id]

            for f in fields:
                f.setReadOnly(True)  # Сразу запрещаем редактирование
                f.setStyleSheet("background-color: #2b2b2b; color: #aaaaaa; border: 1px solid #555;")

            header_layout.addWidget(QLabel("Имя:"))
            header_layout.addWidget(edit_username)
            header_layout.addWidget(QLabel("Почта:"))
            header_layout.addWidget(edit_email)
            header_layout.addWidget(QLabel("Пароль:"))
            header_layout.addWidget(edit_password)
            header_layout.addWidget(QLabel(f"Роль: {user.get('role_name')}"))
            header_layout.addWidget(QLabel("ID:"))
            header_layout.addWidget(edit_role_id)

            btn = QPushButton("Редактировать")
            btn.setFixedWidth(120)

            delete_btn = QPushButton("Удалить")
            delete_btn.setFixedWidth(120)

            user_id = user.get('id')
            btn.clicked.connect(lambda checked, b=btn, f_list=fields, u_id=user_id:
                                self.toggle_edit(b, f_list, u_id))

            delete_btn.clicked.connect(lambda checked, u_id=user_id: self.delete_user(u_id))

            header_layout.addWidget(btn)
            header_layout.addWidget(delete_btn)

            self.users_list_layout.addWidget(row_widget)

    def load_products(self):
        while self.products_list_layout.count():
            item = self.products_list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        products = db.get_products()

        add_card = QFrame()
        add_card.setFixedHeight(100)
        add_card.setStyleSheet("background-color: #264d2f; border-radius: 10px; border: 2px dashed #4caf50;")
        add_l = QHBoxLayout(add_card)

        an = QLineEdit()
        an.setPlaceholderText("Название")
        ap = QLineEdit()
        ap.setPlaceholderText("Цена")
        asq = QLineEdit()
        asq.setPlaceholderText("Кол-во")
        ads = QLineEdit()
        ads.setPlaceholderText("Описание")
        asi = QLineEdit()
        asi.setPlaceholderText("Размер")

        btn_add_p = QPushButton("➕ Создать товар")
        btn_add_p.setFixedSize(150, 40)
        btn_add_p.setStyleSheet("background-color: #4caf50; color: white; border: none;")

        def confirm_add_product():
            if db.add_product(an.text(), ap.text(), asq.text(), ads.text(), asi.text(), "public/img/default.jpg"):
                self.load_products()

        btn_add_p.clicked.connect(confirm_add_product)

        for w in [an, ap, asq, ads, asi]: add_l.addWidget(w)
        add_l.addWidget(btn_add_p)
        self.products_list_layout.addWidget(add_card)

        for product in products:
            product_id = product.get('id')

            card = QFrame()
            card.setFixedHeight(160)  # Фиксируем высоту, чтобы не "плыло"
            card.setStyleSheet("""
                QFrame {
                    background-color: #1a3320; 
                    border-radius: 10px;
                    border: 1px solid #2d5a35;
                }
                QLabel { color: white; border: none; font-size: 13px; }
                QLineEdit { 
                    background-color: #0d1a10; 
                    color: #00ff00; 
                    border: 1px solid #2d5a35;
                    border-radius: 4px;
                    padding: 3px;
                }
            """)

            main_h_layout = QHBoxLayout(card)
            main_h_layout.setContentsMargins(15, 10, 15, 10)
            main_h_layout.setSpacing(20)

            img_box = QVBoxLayout()
            img_label = QLabel()
            img_label.setFixedSize(120, 100)
            img_label.setStyleSheet("background-color: white; border-radius: 5px;")
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            raw_path = product.get('image_url', '')
            full_path = os.path.join(os.getcwd(), raw_path.replace('/', os.sep).lstrip(os.sep))

            if os.path.exists(full_path) and raw_path:
                pix = QPixmap(full_path).scaled(110, 90, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation)
                img_label.setPixmap(pix)
            else:
                img_label.setText("📦")

            btn_img = QPushButton("📸 Сменить фото")
            btn_img.setStyleSheet("background-color: #333; font-size: 10px; height: 20px;")
            btn_img.clicked.connect(lambda ch, p_id=product_id: self.change_image(p_id))

            img_box.addWidget(img_label)
            img_box.addWidget(btn_img)
            main_h_layout.addLayout(img_box)

            info_v_layout = QVBoxLayout()

            edit_name = QLineEdit(str(product.get('name', '')))
            edit_name.setStyleSheet("font-size: 16px; font-weight: bold; border: none; background: transparent;")

            edit_desc = QLineEdit(str(product.get('description', '')))
            edit_desc.setStyleSheet("color: #aaa; font-size: 11px; border: none; background: transparent;")

            details_h_layout = QHBoxLayout()

            edit_price = QLineEdit(str(product.get('price', '')))
            edit_price.setFixedWidth(80)

            edit_stock = QLineEdit(str(product.get('stock_quantity', '')))
            edit_stock.setFixedWidth(50)

            edit_size = QLineEdit(str(product.get('size', '')))
            edit_size.setFixedWidth(40)

            details_h_layout.addWidget(QLabel("Цена:"))
            details_h_layout.addWidget(edit_price)
            details_h_layout.addWidget(QLabel("Склад:"))
            details_h_layout.addWidget(edit_stock)
            details_h_layout.addWidget(QLabel("Размер:"))
            details_h_layout.addWidget(edit_size)
            details_h_layout.addStretch()

            info_v_layout.addWidget(edit_name)
            info_v_layout.addWidget(edit_desc)
            info_v_layout.addLayout(details_h_layout)
            main_h_layout.addLayout(info_v_layout, stretch=1)

            btns_v_layout = QVBoxLayout()

            edit_img_path = QLineEdit(raw_path)
            edit_img_path.setVisible(False)

            fields = [edit_name, edit_price, edit_stock, edit_desc, edit_size, edit_img_path]
            for f in fields: f.setReadOnly(True)

            btn_edit = QPushButton("✎ Редактировать")
            btn_edit.setFixedSize(130, 35)
            btn_edit.setStyleSheet("background-color: #444; border: 1px solid #666;")
            btn_edit.clicked.connect(lambda ch, b=btn_edit, f_list=fields, p_id=product_id:
                                     self.toggle_edit_product(b, f_list, p_id))

            btn_del = QPushButton("🗑 Удалить")
            btn_del.setFixedSize(130, 35)
            btn_del.setStyleSheet("background-color: #722f2f;")
            btn_del.clicked.connect(lambda chekced, p_id=product_id:self.delete_product(p_id))

            btns_v_layout.addWidget(btn_edit)
            btns_v_layout.addWidget(btn_del)
            main_h_layout.addLayout(btns_v_layout)

            self.products_list_layout.addWidget(card)

    def save_user_data(self, user_id, username, email, password, role_id):
        success = db.update_user(user_id, username, email, role_id, password)
        if success:
            print("Обновлено!")
            self.load_users()  # <--- ВОТ ЗДЕСЬ мы заново перерисовываем список!
        else:
            print("Ошибка обновления")

    def clear_sub_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self.clear_sub_layout(item.layout())

    def toggle_edit(self, button, fields, user_id):
        if button.text() == "Редактировать":
            for f in fields:
                f.setReadOnly(False)
                f.setStyleSheet("background-color: #3b3b3b; color: white; border: 1px solid #0078d7;")
            button.setText("Сохранить")
            button.setStyleSheet("background-color: #004a8d; color: white;")
        else:
            u, e, p, r = [f.text().strip() for f in fields]

            if db.update_user(user_id, u, e, r, p):
                print(f"ID {user_id} обновлен")
                self.load_users()
            else:
                print("Ошибка сохранения")

    def delete_user(self, user_id):
        db.delete_user(user_id)
        self.load_users()

    def toggle_edit_product(self, button, fields, product_id):
        if button.text() == "✎ Редактировать":
            for f in fields:
                f.setReadOnly(False)
                if f.isVisible():
                    f.setStyleSheet("background-color: #3b3b3b; color: white; border: 1px solid #0078d7;")
            button.setText("💾 Сохранить")
        else:
            n, p, s, d, si, img = [f.text().strip() for f in fields]

            if db.update_products(product_id, n, p, s, d, si, img):
                self.load_products()
            else:
                print("Ошибка сохранения")

    def change_image(self, product_id):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            file_name = os.path.basename(file_path)
            destination_dir = os.path.join(os.getcwd(), "public", "img")
            os.makedirs(destination_dir, exist_ok=True)

            destination = os.path.join(destination_dir, file_name)

            import shutil
            shutil.copy(file_path, destination)

            db_path = f"public/img/{file_name}"
            if db.update_product_image(product_id, db_path):
                print(f"Картинка обновлена для ID {product_id}")
                self.load_products()  # Перерисовываем список

    def delete_product(self, product_id):
        db.delete_product(product_id)
        self.load_products()