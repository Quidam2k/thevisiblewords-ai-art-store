import requests
import pandas as pd
import base64
import os
from PIL import Image  # Import the Python Imaging Library

# Set your API credentials
access_token = "REDACTED"
# doesn't change from product to product
shop_id = "REDACTED"
target_pixels_width = 4065  # THESE CHANGE FOR DIFFERENT PRODUCTS
target_pixels_height = 2850
blueprint_id = 976
print_provider_id = 92

# Set the URL for the API endpoints
base_url = "https://api.printify.com/v1"
upload_url = f"{base_url}/uploads/images.json"
product_url = f"{base_url}/shops/{shop_id}/products.json"
variants_url = f"{base_url}/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"

# Load the CSV file
csv_path = "product_information.csv"  # Update this to your CSV file path
image_df = pd.read_csv(csv_path)

# Set headers for requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Get the variant IDs for the given blueprint and print provider
response = requests.get(variants_url, headers=headers)
variants = response.json()

for idx, row in image_df.iterrows():
    with Image.open(row['local_path']) as img:
        img_width, img_height = img.size
        img_aspect = img_width / img_height
        target_aspect = target_pixels_width / target_pixels_height
        print(f"Image dimensions: {img_width}x{img_height}")  # Debug print
        print(f"Image aspect ratio: {img_aspect}, Target aspect ratio: {target_aspect}")  # Debug print

        if img_aspect > target_aspect:
            # Image is wider than target; scale based on width to fill horizontally
            scale = target_pixels_width / img_width
        else:
            # Image is taller than target; scale based on height to fill vertically
            scale = target_pixels_height / img_height

        print(f"Image scaled at: {scale}")  # Debug print

    # Convert the image to Base64
    with open(row['local_path'], "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Upload the image to the Printify media library
    data = {
        "file_name": row['file_name'],
        "contents": img_b64
    }
    response = requests.post(upload_url, headers=headers, json=data)
    image_id = response.json()["id"]

    # Create the product with the uploaded image
    data = {
        "title": row['title'],
        "description": row['description'],
        "tags": row['tags'].split(', '),  # Assuming tags are comma-separated in the CSV
        "blueprint_id": blueprint_id,  # Replace with the actual blueprint ID
        "print_provider_id": print_provider_id,
        "variants": [],
        "print_areas": []
    }

    for variant in variants:
        variant_id = variant["id"]
        variant_width = variant["printAreaWidth"]
        variant_height = variant["printAreaHeight"]
        variant_aspect = variant_width / variant_height

        if img_aspect > variant_aspect:
            # Image is wider than variant; scale based on width to fill horizontally
            variant_scale = variant_width / img_width
        else:
            # Image is taller than variant; scale based on height to fill vertically
            variant_scale = variant_height / img_height

        data["variants"].append({
            "id": variant_id,
            "price": 1499,
            "is_enabled": True
        })

        data["print_areas"].append({
            "variant_ids": [variant_id],
            "placeholders": [
                {