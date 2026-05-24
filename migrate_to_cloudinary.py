import os
import json
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load credentials from .env file (safer)
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Configuration
DATA_JSON_PATH = 'data.json'  # Path to your original fixture
MEDIA_ROOT = 'media'          # Path to your local media folder
OUTPUT_FILE = 'data_migrated.json' # Output file name

def upload_image(local_path):
    """Upload a single image to Cloudinary and return its secure URL."""
    full_local_path = os.path.join(MEDIA_ROOT, local_path)
    if not os.path.exists(full_local_path):
        print(f"Warning: Could not find file {full_local_path}. Skipping...")
        return None

    # Upload the file to a 'django_migrated' folder in Cloudinary for organization
    upload_result = cloudinary.uploader.upload(full_local_path, folder="django_migrated")
    print(f"Uploaded {full_local_path} -> {upload_result['secure_url']}")
    return upload_result['secure_url']

def process_fixture(data):
    """Recursively process the JSON fixture and upload image fields."""
    if isinstance(data, dict):
        # If this is a model instance with fields, check for specific image fields
        if 'model' in data and 'fields' in data:
            fields = data['fields']
            # Check for common model fields that store images
            # Add any other fields from your data.json here
            if 'image' in fields and fields['image']:
                print(f"Processing image in model {data['model']}")
                new_url = upload_image(fields['image'])
                if new_url:
                    fields['image'] = new_url
            if 'profile_picture' in fields and fields['profile_picture']:
                print(f"Processing profile_picture in model {data['model']}")
                new_url = upload_image(fields['profile_picture'])
                if new_url:
                    fields['profile_picture'] = new_url
        # Recurse into nested dictionaries
        for value in data.values():
            process_fixture(value)
    elif isinstance(data, list):
        # Recurse into lists
        for item in data:
            process_fixture(item)

if __name__ == '__main__':
    print("Loading fixture...")
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        fixture_data = json.load(f)

    print("Processing fixture and uploading images...")
    process_fixture(fixture_data)

    print(f"Saving migrated fixture to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixture_data, f, indent=2)

    print("Migration complete!")