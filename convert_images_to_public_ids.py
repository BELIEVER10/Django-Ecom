import json
import re
import os

FIXTURE_PATH = 'store/fixtures/data_migrated.json'
OUTPUT_PATH = 'store/fixtures/data_migrated.json'  # overwrite after backup

# Models and their image field names
MODEL_FIELDS = {
    'store.product': ['image'],
    'store.productgallery': ['image'],
    'accounts.userprofile': ['profile_picture'],
    'store.carouselitem': ['image'],
    'category.leftbanner': ['image'],
    'category.rightbanner': ['image'],
    # 'category.category': ['category_image'],  # currently local path, skip
}

def extract_public_id(url):
    """Convert full Cloudinary URL to public ID (without extension)."""
    if not url or not isinstance(url, str):
        return url
    # Pattern: https://res.cloudinary.com/.../upload/(v\d+/)?(.*)
    # The public ID is the part after '/upload/' (optionally after version number)
    match = re.search(r'/upload/(?:v\d+/)?(.+)', url)
    if match:
        public_id = match.group(1)
        # Remove file extension (e.g., .jpg, .png)
        if '.' in public_id:
            public_id = public_id.rsplit('.', 1)[0]
        return public_id
    return url  # leave unchanged if not a Cloudinary URL

def main():
    if not os.path.exists(FIXTURE_PATH):
        print(f"❌ Fixture not found at {FIXTURE_PATH}")
        return

    with open(FIXTURE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0

    for item in data:
        model = item.get('model')
        if model in MODEL_FIELDS:
            fields = item.get('fields', {})
            for field_name in MODEL_FIELDS[model]:
                if field_name in fields and fields[field_name]:
                    old_value = fields[field_name]
                    new_value = extract_public_id(old_value)
                    if new_value != old_value:
                        fields[field_name] = new_value
                        updated_count += 1
                        print(f"✅ {model} pk={item['pk']} {field_name}: {old_value[:60]}... → {new_value}")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"\n🎉 Conversion complete. {updated_count} image fields updated.")
    print("⚠️ Remember to:")
    print("   1. Configure Cloudinary storage in settings.py (DEFAULT_FILE_STORAGE, CLOUDINARY_STORAGE).")
    print("   2. Set Cloudinary environment variables on Render.")
    print("   3. Redeploy your app.")

if __name__ == '__main__':
    main()