import os
import shutil
import sqlite3

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QLabel,
    QListWidgetItem, QFileDialog, QPushButton, QLineEdit, QCheckBox,
    QMessageBox, QComboBox, QInputDialog
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize

from image_loader import scan_folder, get_thumbnail, get_exif_data


DB_PATH = "catalog.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            image TEXT,
            tag TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            image TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Imágenes - Mariano Edition")
        self.resize(1300, 750)

        init_db()

        self.current_folder = None
        self.current_image = None

        main_layout = QHBoxLayout(self)

        # Panel izquierdo
        left_panel = QVBoxLayout()

        self.folder_btn = QPushButton("📁 Elegir carpeta")
        self.folder_btn.clicked.connect(self.choose_folder)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar por nombre o etiqueta...")
        self.search_box.textChanged.connect(self.apply_search)

        self.show_favorites_btn = QPushButton("⭐ Ver favoritos")
        self.show_favorites_btn.clicked.connect(self.show_favorites)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Orden: nombre", "Orden: fecha", "Orden: tamaño"])
        self.sort_combo.currentIndexChanged.connect(self.reload_sorted)

        self.folder_list = QListWidget()

        left_panel.addWidget(self.folder_btn)
        left_panel.addWidget(self.search_box)
        left_panel.addWidget(self.show_favorites_btn)
        left_panel.addWidget(self.sort_combo)
        left_panel.addWidget(self.folder_list)

        # Grid de thumbnails
        self.grid = QListWidget()
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setIconSize(QSize(150, 150))
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setSelectionMode(QListWidget.ExtendedSelection)
        self.grid.itemClicked.connect(self.show_preview)

        # Panel derecho
        right_panel = QVBoxLayout()

        self.preview = QLabel("Selecciona una imagen")
        self.preview.setAlignment(Qt.AlignCenter)

        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Añadir etiqueta y pulsar Enter")
        self.tag_input.returnPressed.connect(self.add_tag)

        self.tags_label = QLabel("Etiquetas: -")

        self.favorite_check = QCheckBox("⭐ Marcar como favorito")
        self.favorite_check.stateChanged.connect(self.toggle_favorite)

        self.exif_label = QLabel("EXIF: -")
        self.exif_label.setWordWrap(True)

        self.export_btn = QPushButton("📤 Exportar seleccionadas...")
        self.export_btn.clicked.connect(self.export_selected)

        self.delete_btn = QPushButton("🗑️ Eliminar imagen actual")
        self.delete_btn.clicked.connect(self.delete_current)

        self.rename_btn = QPushButton("✏️ Renombrar imagen actual")
        self.rename_btn.clicked.connect(self.rename_current)

        right_panel.addWidget(self.preview, stretch=3)
        right_panel.addWidget(self.tags_label)
        right_panel.addWidget(self.tag_input)
        right_panel.addWidget(self.favorite_check)
        right_panel.addWidget(self.exif_label, stretch=2)
        right_panel.addWidget(self.export_btn)
        right_panel.addWidget(self.delete_btn)
        right_panel.addWidget(self.rename_btn)

        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.grid, 3)
        main_layout.addLayout(right_panel, 2)

        self.apply_dark_theme()

    # --------------------
    # MODO OSCURO
    # --------------------
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: Segoe UI;
            }
            QListWidget {
                background-color: #252525;
            }
            QLineEdit {
                background-color: #2b2b2b;
                border: 1px solid #3a3a3a;
                padding: 4px;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)

    # --------------------
    # CARGA DE CARPETA
    # --------------------
    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona carpeta")
        if folder:
            self.current_folder = folder
            self.folder_list.addItem(folder)
            self.load_images(folder)

    def reload_sorted(self):
        if self.current_folder:
            self.load_images(self.current_folder)

    def load_images(self, folder):
        self.grid.clear()
        images = scan_folder(folder)

        mode = self.sort_combo.currentIndex()

        if mode == 0:
            images.sort(key=lambda p: os.path.basename(p).lower())
        elif mode == 1:
            images.sort(key=lambda p: os.path.getmtime(p))
        elif mode == 2:
            images.sort(key=lambda p: os.path.getsize(p))

        for img in images:
            thumb = get_thumbnail(img)
            item = QListWidgetItem(QIcon(thumb), os.path.basename(img))
            item.setData(Qt.UserRole, img)
            self.grid.addItem(item)

    # --------------------
    # BÚSQUEDA
    # --------------------
    def apply_search(self):
        text = self.search_box.text().strip().lower()
        if not self.current_folder:
            return

        self.grid.clear()
        images = scan_folder(self.current_folder)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        tagged_images = set()
        if text:
            for row in c.execute("SELECT image FROM tags WHERE LOWER(tag) LIKE ?", (f"%{text}%",)):
                tagged_images.add(row[0])

        conn.close()

        for img in images:
            name = os.path.basename(img).lower()
            if text:
                if text in name or img in tagged_images:
                    thumb = get_thumbnail(img)
                    item = QListWidgetItem(QIcon(thumb), os.path.basename(img))
                    item.setData(Qt.UserRole, img)
                    self.grid.addItem(item)
            else:
                thumb = get_thumbnail(img)
                item = QListWidgetItem(QIcon(thumb), os.path.basename(img))
                item.setData(Qt.UserRole, img)
                self.grid.addItem(item)

    # --------------------
    # FAVORITOS
    # --------------------
    def show_favorites(self):
        self.grid.clear()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        rows = c.execute("SELECT image FROM favorites").fetchall()
        conn.close()

        for (img,) in rows:
            if os.path.exists(img):
                thumb = get_thumbnail(img)
                item = QListWidgetItem(QIcon(thumb), os.path.basename(img))
                item.setData(Qt.UserRole, img)
                self.grid.addItem(item)

    # --------------------
    # VISTA PREVIA
    # --------------------
    def show_preview(self, item):
        img_path = item.data(Qt.UserRole)
        self.current_image = img_path

        pix = QPixmap(img_path)
        self.preview.setPixmap(pix.scaled(
            self.preview.width(),
            self.preview.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

        self.update_tags_label()
        self.update_favorite_check()
        self.update_exif_label()

    # --------------------
    # TAGS
    # --------------------
    def update_tags_label(self):
        if not self.current_image:
            self.tags_label.setText("Etiquetas: -")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        tags = [row[0] for row in c.execute("SELECT tag FROM tags WHERE image=?", (self.current_image,))]
        conn.close()

        if tags:
            self.tags_label.setText("Etiquetas: " + ", ".join(tags))
        else:
            self.tags_label.setText("Etiquetas: -")

    def add_tag(self):
        if not self.current_image:
            return

        tag = self.tag_input.text().strip()
        if not tag:
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO tags (image, tag) VALUES (?, ?)", (self.current_image, tag))
        conn.commit()
        conn.close()

        self.tag_input.clear()
        self.update_tags_label()

    # --------------------
    # FAVORITOS
    # --------------------
    def update_favorite_check(self):
        if not self.current_image:
            self.favorite_check.setChecked(False)
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        row = c.execute("SELECT image FROM favorites WHERE image=?", (self.current_image,)).fetchone()
        conn.close()

        self.favorite_check.blockSignals(True)
        self.favorite_check.setChecked(row is not None)
        self.favorite_check.blockSignals(False)

    def toggle_favorite(self, state):
        if not self.current_image:
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if state == Qt.Checked:
            c.execute("INSERT OR IGNORE INTO favorites (image) VALUES (?)", (self.current_image,))
        else:
            c.execute("DELETE FROM favorites WHERE image=?", (self.current_image,))
        conn.commit()
        conn.close()

    # --------------------
    # EXIF
    # --------------------
    def update_exif_label(self):
        if not self.current_image:
            self.exif_label.setText("EXIF: -")
            return

        exif = get_exif_data(self.current_image)
        if not exif:
            self.exif_label.setText("EXIF: (sin datos)")
            return

        fields = []
        for key in ("DateTime", "Model", "Make", "Orientation", "ExifVersion"):
            if key in exif:
                fields.append(f"{key}: {exif[key]}")

        if not fields:
            for i, (k, v) in enumerate(exif.items()):
                if i >= 6:
                    break
                fields.append(f"{k}: {v}")

        self.exif_label.setText("EXIF:\n" + "\n".join(fields))

    # --------------------
    # EXPORTAR
    # --------------------
    def export_selected(self):
        items = self.grid.selectedItems()
        if not items:
            QMessageBox.information(self, "Exportar", "No hay imágenes seleccionadas.")
            return

        dest = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de destino")
        if not dest:
            return

        for item in items:
            img_path = item.data(Qt.UserRole)
            try:
                shutil.copy(img_path, dest)
            except Exception as e:
                print("Error copiando", img_path, e)

        QMessageBox.information(self, "Exportar", "Imágenes exportadas correctamente.")

    # --------------------
    # ELIMINAR
    # --------------------
    def delete_current(self):
        if not self.current_image:
            return

        reply = QMessageBox.question(
            self,
            "Eliminar imagen",
            f"¿Seguro que quieres eliminar:\n{self.current_image}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            os.remove(self.current_image)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo eliminar:\n{e}")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM tags WHERE image=?", (self.current_image,))
        c.execute("DELETE FROM favorites WHERE image=?", (self.current_image,))
        conn.commit()
        conn.close()

        name = os.path.basename(self.current_image)
        thumb_path = os.path.join("cache", name + ".thumb.jpg")
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

        self.current_image = None
        self.preview.clear()
        self.tags_label.setText("Etiquetas: -")
        self.favorite_check.setChecked(False)
        self.exif_label.setText("EXIF: -")

        if self.current_folder:
            self.load_images(self.current_folder)

    # --------------------
    # RENOMBRAR
    # --------------------
    def rename_current(self):
        if not self.current_image:
            return

        old_path = self.current_image
        old_name = os.path.basename(old_path)

        new_name, ok = QInputDialog.getText(
            self,
            "Renombrar imagen",
            "Nuevo nombre (sin ruta):",
            text=old_name
        )

        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()
        new_path = os.path.join(os.path.dirname(old_path), new_name)

        try:
            os.rename(old_path, new_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo renombrar:\n{e}")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE tags SET image=? WHERE image=?", (new_path, old_path))
        c.execute("UPDATE favorites SET image=? WHERE image=?", (new_path, old_path))
        conn.commit()
        conn.close()

        self.current_image = new_path

        if self.current_folder:
            self.load_images(self.current_folder)
