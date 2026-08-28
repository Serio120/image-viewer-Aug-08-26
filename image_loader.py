import os
import glob
from PIL import Image, ExifTags

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def scan_folder(folder):
    images = glob.glob(os.path.join(folder, "*.jpg")) + glob.glob(os.path.join(folder, "*.png"))
    return images

def get_thumbnail(path, size=(200, 200)):
    name = os.path.basename(path)
    thumb_path = os.path.join(CACHE_DIR, name + ".thumb.jpg")

    if os.path.exists(thumb_path):
        return thumb_path

    try:
        img = Image.open(path)
        img.thumbnail(size)
        img.save(thumb_path)
        return thumb_path
    except:
        return path

def get_exif_data(path):
    try:
        img = Image.open(path)
        exif_raw = img._getexif()
        if not exif_raw:
            return {}

        exif = {}
        for tag_id, value in exif_raw.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            exif[tag] = value
        return exif
    except:
        return {}
