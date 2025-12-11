# utils/cloudinary.py

import cloudinary
import cloudinary.uploader
import os

from dotenv import load_dotenv
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD"),
    api_key=os.getenv("CLOUDINARY_KEY"),
    api_secret=os.getenv("CLOUDINARY_SECRET"),
    secure=True
)

def upload_profile_photo(file):
    """Uploads a file-like object and returns the secure URL."""
    result = cloudinary.uploader.upload(file, folder="physiocheck/profiles", resource_type="image")
    return result.get("secure_url")
