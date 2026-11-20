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

```bash
git clone https://github.com/Serio120/image-viewer-Aug-08-26.git
cd image-viewer-Aug-08-26
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Windows CMD:

```bat
venv\Scripts\activate.bat
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install PyQt5 Pillow
```

---

## ▶️ Ejecución

Desde la carpeta raíz del proyecto, ejecuta:

```bash
python main.py
```

La aplicación creará automáticamente el archivo local `catalog.db` la primera vez que se inicie. No es necesario descargar, crear ni configurar manualmente esa base de datos.

### ¿Por qué no se incluye `catalog.db` en Git?

La base de datos almacena las etiquetas y los favoritos asociados a las rutas de las imágenes del equipo donde se utiliza la aplicación. Por eso, cada usuario debe tener su propia base de datos local y no compartirla en el repositorio.

En el primer arranque, la función `init_db()` de `ui.py` ejecuta `CREATE TABLE IF NOT EXISTS` para crear las tablas `tags` y `favorites`. La base de datos empieza vacía; las etiquetas y favoritos se guardan localmente a medida que se utilizan esas funciones.

**Importante:** ejecuta `python main.py` desde la carpeta raíz del proyecto. La aplicación utiliza la ruta relativa `catalog.db`, por lo que SQLite creará el archivo en el directorio de trabajo actual.

Si eliminas `catalog.db`, al volver a iniciar la aplicación se generará otra base de datos vacía. Las etiquetas y favoritos guardados en la base de datos anterior no se recuperarán.

---

## 📁 Estructura del proyecto

```
image-viewer-Aug-08-26/
│
├── main.py            # Punto de entrada
├── ui.py              # Interfaz y lógica de interacción
├── image_loader.py    # Carga de imágenes, thumbnails y EXIF
├── catalog.db         # Se genera localmente al iniciar (no se versiona)
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
