import os
from PIL import Image, ExifTags
import requests
import base64
import logging
import json
from utils import load_config
import warnings

config = load_config()
access_token = config["access_token"]
shop_id = config["shop_id"]

base_url = "https://api.printify.com/v1"
upload_url = f"{base_url}/uploads/images.json"
product_url = f"{base_url}/shops/{shop_id}/products.json"

log_file = 'printify_upload.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

Image.MAX_IMAGE_PIXELS = 933120000  # Roughly 30000x30000 pixels

def extract_prompt_from_image(image_path):
    with Image.open(image_path) as img:
        exif_data = img._getexif()
        if not exif_data:
            return "No prompt found"
        for tag, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            if tag_name == 'ImageDescription':
                return value
    return "No prompt found"

def upload_products(selected_products, image_directory, progress_callback=None):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    total_files = len([f for f in os.listdir(image_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    processed_files = 0
    error_summary = []

    for record in selected_products:
        blueprint_id = record['blueprint_id']
        print_provider_id = record['provider']['id']

        variants_url = f"{base_url}/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"
        response = requests.get(variants_url, headers=headers)

        if response.status_code != 200:
            logging.error(f"API request failed with status code {response.status_code}: {response.text}")
            continue

        try:
            variants = response.json().get('variants', [])
            if not variants:
                raise ValueError("No variants found in the response.")
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Error with variants data: {str(e)}")
            continue

        for image_file in os.listdir(image_directory):
            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            processed_files += 1
            if progress_callback:
                progress_callback(processed_files / total_files * 100)

            image_path = os.path.join(image_directory, image_file)
            prompt = extract_prompt_from_image(image_path)
            title = prompt.split('.')[0]
            description = prompt

            try:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    with Image.open(image_path) as img:
                        img_width, img_height = img.size
                    if len(w) > 0 and issubclass(w[-1].category, Image.DecompressionBombWarning):
                        error_msg = f"Image size for {image_file} ({img_width}x{img_height} pixels) exceeds the recommended limit. Skipping this image."
                        logging.warning(error_msg)
                        error_summary.append(error_msg)
                        continue

                with open(image_path, "rb") as img_file:
                    img_b64 = base64.b64encode(img_file.read()).decode('utf-8')

                data = {
                    "file_name": os.path.basename(image_path),
                    "contents": img_b64
                }
                response = requests.post(upload_url, headers=headers, json=data)
                
                if response.status_code < 200 or response.status_code >= 300:
                    error_msg = f"Failed to upload image {image_file}. Server responded with: {response.text}"
                    logging.error(error_msg)
                    error_summary.append(error_msg)
                    continue

                image_id = response.json()["id"]
                preview_url = response.json()["preview_url"]

                data = {
                    "title": title,
                    "description": description + f"\n\nFull artwork:\n<img src='{preview_url}' alt='Full Artwork'>",
                    "tags": [],
                    "blueprint_id": blueprint_id,
                    "print_provider_id": print_provider_id,
                    "variants": [],
                    "print_areas": []
                }

                for variant in variants:
                    variant_id = variant["id"]
                    for placeholder in variant['placeholders']:
                        if placeholder['position'] == 'front':
                            variant_width = placeholder['width']
                            variant_height = placeholder['height']

                            scale = variant_height / img_height * img_width / variant_width if img_width > img_height else 1.0

                            data["variants"].append({
                                "id": variant_id,
                                "price": 1499,
                                "is_enabled": True
                            })

                            data["print_areas"].append({
                                "variant_ids": [variant_id],
                                "placeholders": [
                                    {
                                        "position": "front",
                                        "images": [
                                            {
                                                "id": image_id,
                                                "x": 0.5,
                                                "y": 0.5,
                                                "scale": scale,
                                                "angle": 0
                                            }
                                        ]
                                    }
                                ]
                            })
                            break

                max_retries = 3
                for retry in range(max_retries):
                    response = requests.post(product_url, headers=headers, json=data)
                    if 200 <= response.status_code < 300:
                        logging.info(f"Product created successfully for image {image_file}!")
                        break
                    elif retry < max_retries - 1:
                        logging.warning(f"Failed to create product for image {image_file}. Retrying ({retry + 1}/{max_retries})...")
                    else:
                        error_msg = f"Failed to create product for image {image_file} after {max_retries} retries. Server responded with: {response.text}"
                        logging.error(error_msg)
                        error_summary.append(error_msg)

            except Exception as e:
                error_msg = f"Error processing image {image_file}: {str(e)}"
                logging.error(error_msg)
                error_summary.append(error_msg)

    logging.info("Upload process completed.")
    return error_summary