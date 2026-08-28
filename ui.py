import os
import shutil
import sqlite3

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QLabel,
    QListWidgetItem, QFileDialog, QPushButton, QLineEdit, QCheckBox,
    QMessageBox
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

        # Panel izquierdo: carpeta + búsqueda
        left_panel = QVBoxLayout()
        self.folder_btn = QPushButton("📁 Elegir carpeta")
        self.folder_btn.clicked.connect(self.choose_folder)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar por nombre o etiqueta...")
        self.search_box.textChanged.connect(self.apply_search)

        self.folder_list = QListWidget()

        left_panel.addWidget(self.folder_btn)
        left_panel.addWidget(self.search_box)
        left_panel.addWidget(self.folder_list)

        # Centro: grid de thumbnails
        self.grid = QListWidget()
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setIconSize(QSize(150, 150))
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setSelectionMode(QListWidget.ExtendedSelection)
        self.grid.itemClicked.connect(self.show_preview)

        # Panel derecho: vista previa + tags + favoritos + EXIF + exportar
        right_panel = QVBoxLayout()

        self.preview = QLabel("Selecciona una imagen")
        self.preview.setAlignment(Qt.AlignCenter)

        # Tags
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Añadir etiqueta y pulsar Enter")
        self.tag_input.returnPressed.connect(self.add_tag)

        self.tags_label = QLabel("Etiquetas: -")

        # Favoritos
        self.favorite_check = QCheckBox("⭐ Marcar como favorito")
        self.favorite_check.stateChanged.connect(self.toggle_favorite)

        # EXIF
        self.exif_label = QLabel("EXIF: -")
        self.exif_label.setWordWrap(True)

        # Exportar
        self.export_btn = QPushButton("📤 Exportar seleccionadas...")
        self.export_btn.clicked.connect(self.export_selected)

        right_panel.addWidget(self.preview, stretch=3)
        right_panel.addWidget(self.tags_label)
        right_panel.addWidget(self.tag_input)
        right_panel.addWidget(self.favorite_check)
        right_panel.addWidget(self.exif_label, stretch=2)
        right_panel.addWidget(self.export_btn)

        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.grid, 3)
        main_layout.addLayout(right_panel, 2)

    # --- Carpeta y carga de imágenes ---

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona carpeta")
        if folder:
            self.current_folder = folder
            self.folder_list.addItem(folder)
            self.load_images(folder)

    def load_images(self, folder):
        self.grid.clear()
        images = scan_folder(folder)

        for img in images:
            thumb = get_thumbnail(img)
            item = QListWidgetItem(QIcon(thumb), os.path.basename(img))
            item.setData(Qt.UserRole, img)
            self.grid.addItem(item)

    # --- Búsqueda ---

    def apply_search(self):
        text = self.search_box.text().strip().lower()
        if not self.current_folder:
            return

        self.grid.clear()
        images = scan_folder(self.current_folder)

        # Filtrar por nombre y por tags
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

    # --- Vista previa + EXIF + tags + favoritos ---

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

        # Tags
        self.update_tags_label()

        # Favorito
        self.update_favorite_check()

        # EXIF
        self.update_exif_label()

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

    def update_exif_label(self):
        if not self.current_image:
            self.exif_label.setText("EXIF: -")
            return

        exif = get_exif_data(self.current_image)
        if not exif:
            self.exif_label.setText("EXIF: (sin datos)")
            return

        # Mostrar algunos campos típicos si existen
        fields = []
        for key in ("DateTime", "Model", "Make", "Orientation", "ExifVersion"):
            if key in exif:
                fields.append(f"{key}: {exif[key]}")

        if not fields:
            # Si no están esos, mostramos los primeros 6 campos
            for i, (k, v) in enumerate(exif.items()):
                if i >= 6:
                    break
                fields.append(f"{k}: {v}")

        self.exif_label.setText("EXIF:\n" + "\n".join(fields))

    # --- Exportar seleccionadas ---

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
