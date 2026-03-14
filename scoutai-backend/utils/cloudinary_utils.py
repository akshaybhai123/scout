import cloudinary
import cloudinary.uploader
import os
from typing import Optional

# Cloudinary configuration should be loaded from environment variables in production
# For now, we provide placeholders that the user will need to fill or set as ENV vars.
# Cloudinary configuration
# Prioritize CLOUDINARY_URL if present, otherwise use individual keys
cloudinary_url = os.environ.get('CLOUDINARY_URL')
if cloudinary_url:
    cloudinary.config(cloudinary_url=cloudinary_url)
else:
    cloudinary.config(
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key = os.environ.get('CLOUDINARY_API_KEY'),
        api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
        secure = True
    )

def upload_to_cloudinary(file_path: str, folder: str = "scoutai") -> Optional[str]:
    """
    Uploads a file to Cloudinary and returns its secure URL.
    
    Args:
        file_path: Local path to the file to upload.
        folder: Cloudinary folder name.
    """
    try:
        # Determine resource type based on extension
        ext = os.path.splitext(file_path)[1].lower()
        resource_type = "video" if ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm'] else "raw" if ext == '.pdf' else "image"
        
        response = cloudinary.uploader.upload(
            file_path, 
            folder=folder,
            resource_type=resource_type
        )
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload error: {str(e)}")
        return None

def is_cloudinary_configured() -> bool:
    """Check if Cloudinary is configured with valid credentials."""
    if os.environ.get('CLOUDINARY_URL'):
        return True
    return all([
        os.environ.get('CLOUDINARY_CLOUD_NAME'),
        os.environ.get('CLOUDINARY_API_KEY'),
        os.environ.get('CLOUDINARY_API_SECRET')
    ])
