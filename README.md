## 📸 Image Manager – Gestor de Imágenes en PyQt5

Aplicación de escritorio para Windows creada en Python + PyQt5 que permite **gestionar, visualizar, etiquetar, buscar y exportar imágenes JPG/PNG**, con soporte para **favoritos**, **miniaturas cacheadas** y **lectura de metadatos EXIF**.

Diseñada para manejar cómodamente entre **1.000 y 2.000 imágenes** sin perder rendimiento.

---

## 🚀 Características

- 📁 Selección de carpetas  
- 🖼️ Grid de miniaturas con caché  
- 🔍 Búsqueda por nombre y etiquetas  
- 🏷️ Sistema de etiquetas (SQLite)  
- ⭐ Marcado de favoritos  
- 🧩 Vista previa con zoom automático  
- 🧾 Lectura de metadatos EXIF  
- 📤 Exportación de imágenes seleccionadas  
- ⚡ Carga rápida gracias a thumbnails cacheados  

---

## 🧱 Tecnologías utilizadas

- **Python 3.11**  
- **PyQt5** (interfaz gráfica)  
- **Pillow** (procesado de imágenes y EXIF)  
- **SQLite** (tags y favoritos)  

---

## 📦 Instalación

### 1. Clonar el repositorio

```
git clone https://github.com/TU_USUARIO/image-manager
cd image-manager
```

### 2. Crear entorno virtual (recomendado)

```
python -m venv venv
```

### 3. Activar entorno virtual

Windows PowerShell:

```
.\venv\Scripts\activate
```

### 4. Instalar dependencias

```
pip install PyQt5 Pillow
```

---

## ▶️ Ejecución

Una vez instalado todo:

```
python main.py
```

La aplicación se abrirá con la interfaz completa.

---

## 📁 Estructura del proyecto

```
image-manager/
│
├── main.py            # Punto de entrada
├── ui.py              # Interfaz y lógica de interacción
├── image_loader.py    # Carga de imágenes, thumbnails y EXIF
├── catalog.db         # Base de datos SQLite (tags y favoritos)
├── cache/             # Miniaturas generadas automáticamente
└── README.md
```

---

## 🧩 Funcionalidades avanzadas

### 🏷️ Etiquetas  
Puedes añadir etiquetas a cada imagen y filtrarlas desde la barra de búsqueda.

### ⭐ Favoritos  
Marca imágenes importantes y accede a ellas rápidamente.

### 🔍 Búsqueda  
Busca por nombre de archivo o por etiquetas.

### 🧾 EXIF  
Muestra información técnica de la imagen si está disponible.

### 📤 Exportación  
Selecciona varias imágenes y expórtalas a otra carpeta.

---

## 📜 Licencia

Este proyecto puede utilizarse libremente para aprendizaje, uso personal o ampliación.

---

## 🤝 Contribuciones

Si deseas mejorar la interfaz, añadir nuevas funciones o optimizar el rendimiento, ¡las contribuciones son bienvenidas!

